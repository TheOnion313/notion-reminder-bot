import pickle
import time
from datetime import datetime

import pytz
from discord.ext import commands, tasks

'''
Notification dictionary format:
_________________________________________________________________________________________
|key               |description                                                         |
|_______________________________________________________________________________________|
|send_hour         | hour value of time to send notification                            |
|---------------------------------------------------------------------------------------|
|send_minute       | minute value of time to send notification                          |
|---------------------------------------------------------------------------------------|
|message           | content of notification message                                    |
|---------------------------------------------------------------------------------------|
|channel_id | ID of target channel to notify in                                         |
|---------------------------------------------------------------------------------------|
|time_stamp        | time stamp of notification creation, used to Identify notifications|
|---------------------------------------------------------------------------------------|
|author            | creator of notification, only he and admins can remove notification|
-----------------------------------------------------------------------------------------
'''

DEFAULT_TIMEZONE = 'UTC'

def add_notification(send_time: str, message: str, channel_id: int, author: int):
    send_hours, send_minutes = [int(i) for i in send_time.split(':')]
    notifications.append(
        {'send_hour': send_hours, 'send_minute': send_minutes, 'message': message, 'channel_id': channel_id,
         'time_stamp': int(time.time()), 'author': author})


def to_str(n: dict):
    return f'Channel: {bot.get_channel(n["channel_id"]).mention}\n'\
           f'Time: {str(n["send_hour"]) + ":" + str(n["send_minute"] if n["send_minute"] > 9 else "0" + str(n["send_minute"]))}\n'\
           f'Message content: "{n["message"]}"\n'\
           f'Time stamp: {n["time_stamp"]}\n'\
           f'Author: {bot.get_user(n["author"]).mention}\n' \
           f'Timezone: {timezones[bot.get_channel(n["channel_id"]).guild.id] if bot.get_channel(n["channel_id"]).guild.id in timezones.keys() else DEFAULT_TIMEZONE}'


def backup():
    with open('backup.p', 'wb') as f:
        l = {'notifications': notifications, 'timezones': timezones}
        pickle.dump(l, f)


def load():
    global notifications, timezones
    with open('backup.p', 'rb') as f:
        l = pickle.load(f)
        timezones = l['timezones']
        notifications = l['notifications']
        backup()


bot = commands.Bot('--')
load()


@tasks.loop(seconds=60)
async def notify():
    await bot.wait_until_ready()
    for n in notifications:
        time = datetime.now(pytz.timezone(timezones[bot.get_channel(n['channel_id']).guild.id] if bot.get_channel(n['channel_id']).guild.id in timezones.keys() else DEFAULT_TIMEZONE))
        if time.hour == n['send_hour'] and time.minute == n['send_minute']:
            message_channel = bot.get_channel(n['channel_id'])
            await message_channel.send(f"{bot.get_user(n['author']).mention} is reminding you:\n{n['message']}")


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

    add_notification(time, message, int(channel_id), ctx.message.author.id)
    await ctx.send(f'Added notification:\n{to_str(notifications[-1])}')
    backup()


@bot.command()
async def remove(ctx, time_stamp):
    for i in time_stamp:
        if i not in '1234567890':
            await ctx.send(f'"{time_stamp}" is not an integer, not to mention not a valid ID.')
            return
    for n in notifications:
        if n['time_stamp'] == int(time_stamp):
            if n['author'] == ctx.message.author.id or ctx.message.author.guild_permissions.administrator:
                notifications.remove(n)
                await ctx.send(f'Removed notification\n{to_str(n)}')
                backup()
                return
            await ctx.send(f'{ctx.author.mention}\nYou Do not have permission to remove that notification!!')
            return
    await ctx.send(f'There is no notification with the time stamp {time_stamp}')


@bot.command()
async def list(ctx):
    msg = ''
    for n in notifications:
        if bot.get_channel(n['channel_id']).guild.id == ctx.message.guild.id:
            msg += to_str(n) + '\n\n'

    if len(msg) == 0:
        await ctx.send('No notifications :(')
        return
    await ctx.send(msg)


@bot.command()
async def timezone(ctx, zone=None):
    if zone == None:
        await ctx.send(f'This guild\'s timezone: {timezones[ctx.message.guild.id] if ctx.message.guild.id in timezones.keys() else f"No timezone set, default is {DEFAULT_TIMEZONE}"}')
        return
    if not ctx.message.author.guild_permissions.administrator:
        await ctx.send(f'{ctx.message.author.mention}\n'
                               f'Only administrators can activate this command.')
        return
    for i in pytz.all_timezones:
        if zone.lower() == i.lower():
            guild = ctx.message.guild.id
            timezones[guild] = i
            await ctx.send(f'{ctx.message.author.mention}\n'
                               f'The timezone has been set!')
            backup()
            return
    else:
        contains = ''
        for tz in pytz.all_timezones:
            split = tz.split('/')
            if zone.lower() in [i.lower() for i in split]:
                contains += tz + '\n'

        if len(contains) == 0:
            await ctx.send(f'{ctx.message.author.mention}\n'
                           f'There is no timezone related to your input.')
            return

        await ctx.send(f'{ctx.message.author.mention}\n'
                               f'Timezones related to your input:\n'
                               f'{contains}\n'
                               f'Please choose one of the above and call the command again.')



bot.run(open('token.txt', 'r').readline())
