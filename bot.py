from datetime import datetime

import discord
from discord.ext import commands, tasks

def add_notification(send_time: str, message: str, channel_id: int):
    send_hours, send_minutes = [int(i) for i in send_time.split(':')]
    notifcations.append({'send_hour': send_hours, 'send_minute': send_minutes, 'message': message, 'target_channel_id': channel_id})

bot = commands.Bot('--')

notifcations = []
add_notification('17:19', 'Hello boyo', 766349625769721888)


@tasks.loop(seconds=60)
async def notify():
    await bot.wait_until_ready()
    time = datetime.now()
    for n in notifcations:
        if time.hour == n['send_hour'] and time.minute == n['send_minute']:
            message_channel = bot.get_channel(n['target_channel_id'])
            print(f"Got channel {message_channel}")
            await message_channel.send(n['message'])

notify.start()

@bot.command()
async def add_notif(ctx, given_name, time, message):
    wanted_channel_id = -1
    for channel in ctx.guild.channels:
        if channel.name == given_name:
            wanted_channel_id = channel.id
    if len(time) != 5 or time[2] != ':' or not all([i in '0123456789' for i in time[:2] + time[3:]]):
        await ctx.send('Time format invalid.')
        return
    if wanted_channel_id == -1:
        await ctx.send(f"Channel #{given_name} doesn't exist")
        return
    await ctx.send(f'Added notification:\nChannel: {bot.get_channel(wanted_channel_id).mention}\nTime: {time}\nMessage content: "{message}"')
    add_notification(time, message, wanted_channel_id)

bot.run(open('token.txt', 'r').readline())
