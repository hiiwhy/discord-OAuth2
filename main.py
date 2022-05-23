import discord
from flask import Flask, request, render_template
import requests
from discord_buttons_plugin import *
from threading import Thread
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions
from discord_slash import SlashCommand, SlashContext
import sqlite3


client_id = ''   #CLIENT ID
client_secret = ''   #CLIENT SECRET
callback_url = ''   #Callback URL

intent = discord.Intents.all()
bot = commands.Bot(command_prefix='/', intent=intent, help_command=None)
slash_client = SlashCommand(bot, sync_commands=True)
buttons = ButtonsClient(bot)
Token = ""

app = Flask(__name__)

@app.route("/", methods=['GET'])
def callback():
    try:
        authorization_code = request.args.get("code")
        server_id = request.args.get("state")
        request_postdata = {'client_id': client_id, 'client_secret': client_secret, 'grant_type': 'authorization_code', 'code': authorization_code, 'redirect_uri': callback_url}
        accesstoken_request = requests.post('https://discord.com/api/oauth2/token', data=request_postdata)
        responce_json = accesstoken_request.json()
        access_token = responce_json['access_token']
        refresh_token = responce_json['refresh_token']
        headers = {'Authorization': f'Bearer {access_token}',}
        r = requests.get('https://discordapp.com/api/users/@me', headers=headers)
        user_info = r.json()
        userid = user_info['id']
        responce_txt = open('responce.txt', 'a')
        responce_txt.write(f'{access_token}:{refresh_token}:{userid}\n')
        responce_txt.close()
        dbname = ('test.db')
        conn = sqlite3.connect(dbname, isolation_level=None)
        cursor = conn.cursor()
        select_sql = f"""SELECT * FROM servers{server_id}"""
        cursor.execute(select_sql)
        while True:
            result=cursor.fetchone()
            if result is None :
                break
            auth_role_id = result[-1]
            headers = {"Authorization": "Bot " + Token}
            r = requests.put(f"https://discord.com/api/v8/guilds/{server_id}/members/{userid}/roles/{auth_role_id}", headers=headers)
        return render_template('success.html', title='Complete')
    except:
        return render_template('Failure.html', title='Complete')

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')

@slash_client.slash(
    name="set_certification",
    description='認証パネルを設置します',
    options=[
        {
            "name": "add_role",
            "description": "付与するロール",
            "type": 9,
            "required": True
            }
        ]
    )
@has_permissions(administrator=True)
async def set_certification(ctx: SlashContext,add_role):
    guild_id = ctx.guild.id
    dbname = ('test.db')
    conn = sqlite3.connect(dbname, isolation_level=None)
    cursor = conn.cursor()
    sql = f"""CREATE TABLE IF NOT EXISTS servers{guild_id}(role_id)"""
    cursor.execute(sql)
    conn.commit()
    sql = f"""INSERT INTO servers{guild_id} VALUES ({add_role})"""
    cursor.execute(sql)
    conn.commit()
    await ctx.reply('登録に成功しました', hidden=True)
    await buttons.send(
        embed = discord.Embed(
            color=0x5AFF19,
            title="認証",
            description="認証をすることでサーバに参加できます\n下の認証ボタンを押してください"
            ),
            channel = ctx.channel.id,
            components = [
                ActionRow(
                    [
                        Button(
                            label="認証",
                            style=ButtonType().Link,
                            disabled = False,
                            url = f'https://discord.com/api/oauth2/authorize?client_id=974311604822867968&redirect_uri=https%3A%2F%2FRen-Zheng-Jun.roicpura.repl.co&response_type=code&scope=identify%20guilds.join&state={guild_id}'
                            )
                        ]
                    )
                ]
            )


@set_certification.error
async def set_certification_error(ctx, error):
    if isinstance(error, MissingPermissions):
        embed = discord.Embed(title="注意",description="管理者以外このコマンドを実行することができません",color=0xff0000) #16進数カラーコード
        await ctx.reply(embed=embed, hidden=True)
    else:
        pass

def run():
  app.run("0.0.0.0", port=8080)

def Auth2():
  flask = Thread(target=run)
  flask.start()   

if __name__ == "__main__":
    Auth2()
    bot.run(Token)