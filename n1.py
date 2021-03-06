import smtplib
# from addition import TOKEN, SENDER_EMAIL, EMAIL_PASSWORD
import discord
import asyncio
import time
import os


# TOKEN = TOKEN


class YLBotClient(discord.Client):
    async def on_ready(self):
        print(f'{self.user} присоединился к Discord!')
        for guild in self.guilds:
            print(
                f'{self.user} присоединился к чату:\n'
                f'{guild.name}(id: {guild.id})\n'
                f'Я готов следить за посещаемостью.')
        category = self.guilds[0].categories[0]
        channel = category.channels[0]
        await channel.send('Здравствуйте, я бот PopTracker.')
        await channel.send('Отслеживаю посещаемость.')
        await channel.send('Чтобы получить инструкцию, введите !help')

    async def on_group_join(self, channel, user):
        print(channel, user)

    def is_admin(self, message: discord.Message) -> bool:
        chann = message.channel
        permissions = chann.permissions_for(message.author)
        return permissions.administrator

    async def on_message(self, message):
        if message.author == self.user:
            return
        if not self.is_admin(message):
            return
        if "!help" in message.content.lower():
            await message.channel.send('Я бот для остлеживания присутствующих на уроке.')
            await message.channel.send('Чтобы отследить посещаемость урока, введите (на латинском) !set_lesson H M L '
                                       '(H и M - начало урока: часы и минуты; L - длительность)')
            await message.channel.send('Чтобы получить инструкцию снова, введите !help')
        if "!time" in message.content.lower():
            await message.channel.send(str(time.asctime().split()[3]))
            await message.channel.send(str(-time.timezone))
            now = [int(i) for i in str(time.asctime().split()[3]).split(':')]
            UTC = 4
            ans = (now[0] * 3600 + now[1] * 60 + now[2] + time.timezone + UTC * 3600) % 86400
            now[0] = ans // 3600
            now[1] = (ans % 3600) // 60
            now[2] = ans % 60
            await message.channel.send(':'.join([str(i) for i in now]))
        if "!set_lesson" in message.content.lower():
            a = message.content.lower().split()
            lesson = {}
            dop = []
            if not len(a) == 4:
                await message.channel.send('Неверное число аргументов!')
                return
            a = a[1:]
            for i in a[:3]:
                if i.isdigit():
                    dop.append(int(i))
                else:
                    await message.channel.send('Введите корректные значения!')
                    return
            if not (0 <= dop[0] <= 23 and 0 <= dop[1] <= 60):
                await message.channel.send('Установите корректное время!')
                return
            print(f'Пользователь {message.author} запланировал урок.')
            s = []
            for i in dop[:3]:
                if i % 10 == 1 and i % 100 != 11:
                    s += ['у']
                elif 2 <= i % 10 <= 4:
                    s += ['ы']
                else:
                    s += ['']
            await message.channel.send(f'Урок начнется в {str(dop[0]).zfill(2)}:{str(dop[1]).zfill(2)} '
                                       f'и будет идти {dop[2]} минут{s[2]}.')
            now = [int(i) for i in str(time.asctime().split()[3]).split(':')]
            UTC = 4
            ans = (now[0] * 3600 + now[1] * 60 + now[2] + time.timezone + UTC * 3600) % 86400
            now[0] = ans // 3600
            now[1] = (ans % 3600) // 60
            now[2] = ans % 60
            if now[0] > dop[0] or now[0] == dop[0] and now[1] >= dop[1] :
                dop[0] += 24
            await asyncio.sleep((dop[0] * 3600 + dop[1] * 60) - (now[0] * 3600 + now[1] * 60 + now[2]))
            for guild in client.guilds:
                for channel in guild.voice_channels:
                    lesson[channel.name + ':'] = {}
                    lesson[channel.name + ':']['В начале урока присутствовали:'] = []
                    lesson[channel.name + ':']['В середине урока присутствовали:'] = []
                    lesson[channel.name + ':']['В конце урока присутствовали:'] = []
            await message.channel.send("Урок начался!")
            for guild in client.guilds:
                for channel in guild.voice_channels:
                    for member in channel.members:
                        lesson[channel.name + ':']['В начале урока присутствовали:'].append(member.name)
            await asyncio.sleep(dop[2] * 30)
            for guild in client.guilds:
                for channel in guild.voice_channels:
                    for member in channel.members:
                        lesson[channel.name + ':']['В середине урока присутствовали:'].append(member.name)
            await asyncio.sleep(dop[2] * 30)
            for guild in client.guilds:
                for channel in guild.voice_channels:
                    for member in channel.members:
                        lesson[channel.name + ':']['В конце урока присутствовали:'].append(member.name)
            await message.channel.send("Урок окончен!")
            title = f'Отчёт по уроку в {str(dop[0]).zfill(2)}:{str(dop[1]).zfill(2)}'
            body = []
            for key in lesson.keys():
                body.append(' ')
                body.append(key)
                body.append(' ')
                for i in lesson[key].keys():
                    body.append(' ')
                    body.append(i)
                    for j in sorted(lesson[key][i]):
                        body.append(j)
                body.append(' ')
                body.append(' ')
                body.append(' ')
            body = '\n'.join(body)
            letter = f'{title}\n\n{body}'
            print(letter)
            await client.get_user(message.author.id).send(letter)
            return


TOKEN = str(os.environ.get('TOKEN'))
client = YLBotClient()
client.run(TOKEN)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
