import os
import asyncio
import discord
from discord.ext import commands

private_rooms = {}

intents = discord.Intents.default()

intents.members = True

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

@bot.event
async def on_ready():

    try:
        synced = await bot.tree.sync()
        print(f"{len(synced)}個のコマンドを同期")
    except Exception as e:
        print(e)
    print(f"ログインしました: {bot.user}")

CATEGORY_ID = 1504725711473217546

@bot.tree.command(name="build",description="プライベートVCを作成")
async def build(interaction: discord.Interaction):

    if interaction.user.id in private_rooms:

        await interaction.response.send_message(
            "既にVCを作成しています",
            ephemeral=True
        )
        return

    category = interaction.guild.get_channel(
        CATEGORY_ID
    )

    overwrites = {

        interaction.guild.default_role:
        discord.PermissionOverwrite(
            view_channel=False,
            connect=False
        ),

        interaction.user:
        discord.PermissionOverwrite(
            view_channel=True,
            connect=True
        )
    }

    channel = await category.create_voice_channel(
        name=f"{interaction.user.name}のVC",
        overwrites=overwrites
    )
    
    private_rooms[interaction.user.id] = channel

    await interaction.response.send_message(
        f"{channel.mention} を作成しました", ephemeral=True
    )

@bot.tree.command(name="end",description="自分のVCを削除")
async def end(interaction: discord.Interaction):

    channel = private_rooms.get(
        interaction.user.id
    )

    # 持ってない
    if channel is None:

        await interaction.response.send_message(
            "VCを持っていません",
            ephemeral=True
        )
        return

    # VC削除
    await channel.delete()

    # データ削除
    del private_rooms[interaction.user.id]

    await interaction.response.send_message(
        f"{interaction.user.name}のVCを削除しました",
        ephemeral=True
    )

@bot.tree.command(name="invite",description="指定した人をVCに招待")
async def invite(interaction: discord.Interaction, user:discord.mention):

    # 自分のVC取得
    channel = private_rooms.get(
        interaction.user.id
    )

    # VC持ってない
    if channel is None:

        await interaction.response.send_message(
            "VCを持っていません",
            ephemeral=True
        )
        return

    # 権限追加
    await channel.set_permissions(
        user,
        view_channel=True,
        connect=True
    )

    await interaction.response.send_message(
        f"{user.mention} を招待しました",
        ephemeral=True
    )

@bot.tree.command(name="invite_role",description="指定したロールをVCに招待")
async def invite_role(interaction: discord.Interaction, role: discord.Role):

    # 自分のVC取得
    channel = private_rooms.get(
        interaction.user.id
    )

    # VC持ってない
    if channel is None:

        await interaction.response.send_message(
            "VCを持っていません",
            ephemeral=True
        )
        return

    # 権限追加
    await channel.set_permissions(
        role,
        view_channel=True,
        connect=True
    )

    await interaction.response.send_message(
        f"{role.mention} を招待しました",
        ephemeral=True
    )

@bot.tree.command(name="kick", description="指定した人のVC参加権限を外す")
async def kick(interaction: discord.Interaction, user: discord.Member):

    channel = private_rooms.get(interaction.user.id)

    if channel is None:
        await interaction.response.send_message(
            "VCを持っていません",
            ephemeral=True
        )
        return

    await channel.set_permissions(
        user,
        overwrite=None
    )

    await interaction.response.send_message(
        f"{user.mention} の参加権限を外しました",
        ephemeral=True
    )

@bot.tree.command(name="kick_role",description="指定したロールのVC参加権限を外ず")
async def kick_role(interaction: discord.Interaction, role: discord.Role):

    # 自分のVC取得
    channel = private_rooms.get(
        interaction.user.id
    )

    # VC持ってない
    if channel is None:

        await interaction.response.send_message(
            "VCを持っていません",
            ephemeral=True
        )
        return

    # 権限追加
    await channel.set_permissions(
        role,
        overwrite=None
    )

    await interaction.response.send_message(
        f"{role.mention}の参加権限を外しました ",
        ephemeral=True
    )

@bot.event
async def on_voice_state_update(
    member,
    before,
    after
):

    # VCから抜けた
    if before.channel:

        channel = before.channel

        # 管理VCか
        if channel in private_rooms.values():

            # 誰もいない
            if len(channel.members) == 0:

                # 10秒待機
                await asyncio.sleep(10)

                # まだ空
                if len(channel.members) == 0:

                    await channel.delete()

                    # 保存削除
                    for user_id, vc in list(private_rooms.items()):

                        if vc == channel:

                            del private_rooms[user_id]
                            break

bot.run(os.getenv("TOKEN"))
