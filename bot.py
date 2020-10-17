import time
from datetime import datetime

from discord.ext import commands, tasks


def add_notification(send_time: str, message: str, channel_id: int):
    send_hours, send_minutes = [int(i) for i in send_time.split(':')]
    notifcations.append(
        {'send_hour': send_hours, 'send_minute': send_minutes, 'message': message, 'target_channel_id': channel_id,
         'time_stamp': int(time.time())})


def to_str(n: dict):
    return f'Channel: {bot.get_channel(n["target_channel_id"]).mention}\n'\
           f'Time: {str(n["send_hour"]) + ":" + str(n["send_minute"])}\n'\
           f'Message content: "{n["message"]}"'


bot = commands.Bot('--')

notifcations = []


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
async def add(ctx, given_name, time, message):
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
    add_notification(time, message, wanted_channel_id)
    await ctx.send(f'Added notification:\n{to_str(notifcations[-1])}')


@bot.command()
async def remove(ctx, time_stamp):
    for n in notifcations:
        if n['time_stamp'] == int(time_stamp):
            notifcations.remove(n)
            await ctx.send(f'Removed notificatoin {to_str(n)}')
            return


bot.run(open('token.txt', 'r').readline())
