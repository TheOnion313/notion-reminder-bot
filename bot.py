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
           f'Message content: "{n["message"]}"\n' \
           f'Time stamp: {n["time_stamp"]}'


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
async def add(ctx, given_name=None, time=None, message=None):
    if given_name == None or time == None or message == None:
        await ctx.send('Not all parameters required were given')
        return

    valid = False
    channel_id = given_name[2:-1]
    for channel in ctx.guild.channels:
        if channel_id == str(channel.id):
            valid = True
    if not valid:
        await ctx.message(f'{ctx.message.autor.mention}\nChannel #{given_name} does not exist')
        return
    if len(time) != 5 or time[2] != ':' or not all([i in '0123456789' for i in time[:2] + time[3:]]):
        await ctx.send('Time format invalid.')
        return
    add_notification(time, message, int(channel_id))
    await ctx.send(f'Added notification:\n{to_str(notifcations[-1])}')


@bot.command()
async def remove(ctx, time_stamp):
    for n in notifcations:
        if n['time_stamp'] == int(time_stamp):
            notifcations.remove(n)
            await ctx.send(f'Removed notification\n{to_str(n)}')
            return

@bot.command()
async def list(ctx):
    msg = ''
    for n in notifcations:
        msg += to_str(n)+'\n\n'

    if len(msg) == 0:
        await ctx.send('No notifications :(')
        return
    await ctx.send(msg)

@bot.command()
async def msg(ctx, channel=None):
    print(channel[2:-1])
    print(channel)


bot.run(open('token.txt', 'r').readline())
