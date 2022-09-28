import discord, time, urllib, random
import settings
from pyquery import PyQuery as pq
from io import BytesIO

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True

client = discord.Client(intents=intents)

birthdays_done = {}
cache = {}

def l2u(s):
    return str(bytes(s, 'latin1'), 'utf-8')

def cached(what, url):
    global cache
    if not cache.get(f'{what}_data') or cache.get(f'{what}_age', 0) + 300 < time.time():
        try:
            newdata = pq(url=url)
            cache[f'{what}_data'] = newdata
        except:
            pass
        cache[f'{what}_age'] = time.time()
    return cache[f'{what}_data']

def getvreme(what='long'): # or long or full
    napoved = cached('napoved', 'https://meteo.arso.gov.si/uploads/probase/www/fproduct/text/sl/fcast_si_text.html')
    podatki = cached('podatki', 'https://meteo.arso.gov.si/uploads/probase/www/observ/surface/text/sl/observation_si_latest.html')
    text_podatki = '\n'
    for location in settings.LOCATIONS:
        line = podatki('td').filter(lambda i, this: location == l2u(pq(this).text()))
        vreme_text = l2u(line.next().next()[0].text)
        if not vreme_text: vreme_text = 'neznano'
        stopinje_text = l2u(line.next().next().next()[0].text)
        if not stopinje_text: stopinje_text = '??'
        text_podatki += location.split()[-1] + ', ' + vreme_text + ', ' + stopinje_text + '°C\n'
    text_vreme = ''
    if what == 'long':
        p = napoved("h2").next().next().next()
        while True:
            el = p[0]
            if el.tag != 'p':
                break
            text_vreme += '\n' + l2u(el.text)
            p = p.next()
    elif what == 'full':
        text_vreme = ''
        p = napoved("h2:first")
        while True:
            el = p[0]
            if el.tag not in ('h2', 'p'):
                break
            text_vreme += '\n' + l2u(el.text)
            p = p.next()
    elif what == 'short':
        text_vreme = l2u(napoved("p:first")[0].text)
    else:
        return 'ne vem kaj je to ' + what + ', lahko je short, long, full'
    return text_podatki + text_vreme

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_presence_update(before, after):
    print(f'{after.display_name} changed presence to {after.raw_status}')
    today = time.strftime('%d-%m')
    year = int(time.strftime('%Y'))
    birthday = settings.BIRTHDAYS.get(after.display_name)
    if birthday == today and birthdays_done.get(after.display_name, 0) < year:
        channel = client.get_channel(895560470210150440)
        birthdays_done[after.display_name] = year
        message = random.choice(settings.BIRTHDAY_MESSAGES)
        await channel.send(f'Zdravo {after.display_name}!\n{message}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.lower().startswith('vreme') and len(message.content.split()) < 3:
        try:
            what = message.content.split()[1]
        except IndexError:
            what = 'long'
        await message.channel.send('```' + getvreme(what) + '```')

    if message.content.lower().startswith('radar') and len(message.content.split()) < 2:
        radar_gif = BytesIO(urllib.request.urlopen('https://meteo.arso.gov.si/uploads/probase/www/observ/radar/si0-rm-anim.gif').read())
        await message.channel.send(file=discord.File(radar_gif, filename='radar.gif'))

client.run(settings.TOKEN)

