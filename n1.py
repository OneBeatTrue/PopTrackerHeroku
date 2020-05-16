import smtplib
from addition import TOKEN, SENDER_EMAIL, EMAIL_PASSWORD
import discord
import asyncio
import time


TOKEN = TOKEN


class YLBotClient(discord.Client):
    async def on_ready(self):
        print(f'{self.user} has connected to Discord!')
        for guild in self.guilds:
            print(
                f'{self.user} has connected to chat:\n'
                f'{guild.name}(id: {guild.id})'
                f'I am ready to to track students.')
        category = self.guilds[0].categories[0]
        channel = category.channels[0]
        # await channel.send('Hello, my name is PopTracker.')
        # await channel.send('I am ready to to track students.')
        # await channel.send('To get the instructions, type !help')
        return

    async def on_group_join(self, channel, user):
        print(channel, user)
        return

    def transliteration(self, st):
        a = {'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'E',
             'Ж': 'Zh', 'З': 'Z', 'И': 'I', 'Й': 'I', 'К': 'K', 'Л': 'L', 'М': 'M',
             'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U',
             'Ф': 'F', 'Х': 'Kh', 'Ц': 'Tc', 'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Shch',
             'Ы': 'Y', 'Э': 'E', 'Ю': 'Iu', 'Я': 'Ia', 'а': 'a', 'б': 'b', 'в': 'v',
             'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e', 'ж': 'zh', 'з': 'z', 'и': 'i',
             'й': 'i', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p',
             'р': 'r', 'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'kh', 'ц': 'tc',
             'ч': 'ch', 'ш': 'sh', 'щ': 'shch', 'ы': 'y', 'э': 'e', 'ю': 'iu', 'я': 'ia'}
        y = []
        w = ''
        s = st
        s = s.split()
        for i in range(len(s)):
            t = s[i]
            for u in range(len(t)):
                if t[u] in a:
                    w += a[t[u]]
                else:
                    if t[u] == 'ъ' or t[u] == 'ь' or t[u] == 'Ъ' or t[u] == 'Ь':
                        continue
                    else:
                        w += t[u]
            if len(w) != 0:
                y.append(w)
                w = ''
        return ' '.join(y)

    def is_admin(self, message: discord.Message) -> bool:
        chann = message.channel
        permissions = chann.permissions_for(message.author)
        return permissions.administrator

    def is_correct_email(self, email):
        if email.count('@') > 1 or email.count('@') == 0:
            return False
        [name, domain] = email.split('@')
        if len(domain) < 3 or len(domain) > 256 or domain.count('.') == 0:
            return False
        includedomain = domain.split('.')
        correctchrlist = list(range(ord('a'), ord('z') + 1))
        correctchrlist.extend([ord('-'), ord('_')])
        correctchrlist.extend(list(range(ord('0'), ord('9') + 1)))
        for k in includedomain:
            if k == '':
                return False
            for n in k:
                if ord(n) not in correctchrlist:
                    return False
            if k[0] == '-' or k[len(k) - 1] == '-':
                return False
        if len(name) > 128:
            return False
        correctchrlist.extend([ord('.'), ord(';'), ord('"')])
        onlyinquoteschrlist = [ord('!'), ord(','), ord(':')]
        correctchrlist.extend(onlyinquoteschrlist)
        if name.count('"') % 2 != 0:
            return False
        doubledot = False
        inquotes = False
        for k in name:
            if k == '"':
                inquotes = not inquotes
            if (ord(k) in onlyinquoteschrlist) and (inquotes == False):
                return False
            if ord(k) not in correctchrlist:
                return False
            if k == '.':
                if doubledot:
                    return False
                else:
                    doubledot = True
        return True

    async def on_message(self, message):
        if message.author == self.user:
            return
        if not self.is_admin(message):
            return
        if "!help" in message.content.lower():
            await message.channel.send('I am a bot that tracks class attendance.')
            await message.channel.send('To make a tracking lesson you need to print !set_lesson H M L E '
                                       '(H and M - time when the lesson should start: hours and minutes; L-duration; '
                                       'E - email address to send the report to)')
            await message.channel.send('To get the instructions again, type !help again.')
        if "!set_lesson" in message.content.lower():
            a = message.content.lower().split()
            lesson = {}
            dop = []
            if not len(a) == 5:
                await message.channel.send('Invalid number of arguments!')
                return
            a = a[1:]
            for i in a[:3]:
                if i.isdigit():
                    dop.append(int(i))
                else:
                    await message.channel.send('Invalid argument values!')
                    return
            dop.append(str(a[3]))
            if not self.is_correct_email(dop[3]):
                await message.channel.send('You are trying to set a wrong email!')
                return
            if not (0 <= dop[0] <= 23 and 0 <= dop[1] <= 60):
                await message.channel.send('You are trying to set a wrong time!')
                return
            print(f'{message.author} set the lesson.')
            s = ['' if i == 1 else 's' for i in dop[:3]]
            await message.channel.send(f'The lesson should start at {dop[0]} hour{s[0]} {dop[1]} '
                                       f'minute{s[1]} and lasts {dop[2]} minute{s[2]}.')
            now = [int(i) for i in str(time.asctime().split()[3]).split(':')]
            if now[0] > dop[0] or now[0] == dop[0] and now[1] >= dop[1] :
                dop[0] += 24
            await asyncio.sleep((dop[0] * 3600 + dop[1] * 60) - (now[0] * 3600 + now[1] * 60 + now[2]))
            lesson['At the beginning of the lesson, there were:'] = []
            lesson['At the middle of the lesson, there were:'] = []
            lesson['At the end of the lesson, there were:'] = []
            await message.channel.send("The lesson has begun!")
            for guild in client.guilds:
                for member in guild.voice_channels[0].members:
                    lesson['At the beginning of the lesson, there were:'].append(member.name)
            await asyncio.sleep(dop[2] * 30)
            for guild in client.guilds:
                for member in guild.voice_channels[0].members:
                    lesson['At the middle of the lesson, there were:'].append(member.name)
            await asyncio.sleep(dop[2] * 30)
            for guild in client.guilds:
                for member in guild.voice_channels[0].members:
                    lesson['At the end of the lesson, there were:'].append(member.name)
            await message.channel.send("The lesson is over!")
            title = f'The report on the lesson that started at {dop[0]}:{dop[1]}'
            body = []
            for key in lesson.keys():
                body.append(key)
                for i in lesson[key]:
                    body.append(self.transliteration(i))
                body.append(' ')
            body = '\n'.join(body)
            letter = f'Subject: {title}\n\n{body}'
            print(letter)
            REC_EMAIL = dop[3]
            SERVER = smtplib.SMTP('smtp.gmail.com', 587)
            SERVER.starttls()
            SERVER.login(SENDER_EMAIL, EMAIL_PASSWORD)
            SERVER.sendmail(SENDER_EMAIL, REC_EMAIL, letter)
            return


client = YLBotClient()
client.run(TOKEN)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
