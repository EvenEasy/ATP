import grequests, asyncio
from bs4 import BeautifulSoup as BS
from pyppeteer import launch, input
from create_bot import bot

class ATP:

    current_games = []
    data = {}
    loop = asyncio.get_event_loop()

    async def follow_start_live(self):
        print("Follow start live")
        browser = await launch()
        page = await browser.newPage()
        await page.goto("https://www.flashscore.ua/tennis/")
        await page.waitFor(3000)
        elems = await page.querySelectorAll('span[class="event__expanderBlock"]')
        for i1,i in enumerate(elems):
            if i1 != 0: await i.click()

        bttn = await page.querySelector('div[class="filters__text filters__text--default"]')
        await bttn.click()

        #bttn = await page.querySelector('button[id="onetrust-accept-btn-handler"]')
        #await bttn.click()


        await page.screenshot(path='photo.jpg')
        while True:
            elements = await page.querySelectorAll('div[class="event__match event__match--live event__match--twoLine"]')
            for element in elements:
                ls = await element.querySelectorAll(['span[class="down"]', 'span[class="up"]'])
                print(ls)
                try:
                    pl1 = await page.evaluate('(element) => element.textContent', ls[0])
                    pl2 = await page.evaluate('(element) => element.textContent', ls[1])
                    pl1 = float(pl1)
                    pl2 = float(pl2)
                except Exception: pass

                a1 = await element.getProperty('id')
                match_code = a1._remoteObject.get('value').split('_')[-1]

                if match_code not in self.current_games:
                    if pl1 >= 1.01 and pl1<=1.50:
                        self.current_games.append(match_code)
                        self.data.update(
                            {f'{match_code}':{'favorite':1, 'coef':pl1}}
                        )
                        self.loop.create_task(self.follow_match(match_code, 0))
                        
                    elif pl2 >= 1.01 and pl2<=1.50:
                        self.current_games.append(match_code)
                        self.data.update(
                            {f'{match_code}':{'favorite':2, 'coef':pl2}}
                        )
                        self.loop.create_task(self.follow_match(match_code, 1))

            await asyncio.sleep(1800)

    async def follow_match(self,match_code : str, favorite : int = 0):
        current_round = 5
        current_set = 0

        last_lost = None


        #await asyncio.sleep(10)
        browser = await launch()
        page = await browser.newPage()
        await page.goto(f"https://www.flashscore.ua/match/{match_code}/#/match-summary/point-by-point/0")
        await page.waitFor(2000)
        '''
        content = await page.content()
        content = content.encode()
        print(content)
        '''
        
        while True:
            is_live = await page.querySelector('a[class="liveBetIcon"]')
            if not is_live:
                print('MATCH FINISHED',is_live, current_set, current_round, last_lost)
                self.current_games.remove(match_code)
                self.data.pop(match_code)
                break

            
            sets = await page.querySelectorAll(['a[class="subTabs__tab selected"]', 'a[class="subTabs__tab"]'])
            current_set = len(sets)-1

            await page.goto(f"https://www.flashscore.ua/match/{match_code}/#/match-summary/point-by-point/{current_set}")
            
            match_historys = await page.querySelectorAll('div[class="matchHistoryRow"]')
            #print(len(match_historys))
            current_round = len(match_historys)

            
            print(is_live, current_set, current_round, last_lost)
            
            try:
                result = [
                await match_historys[current_round-1].querySelector(
                    (
                        'div[class="matchHistoryRow__lostServe matchHistoryRow__green  matchHistoryRow__highlight matchHistoryRow__away"]',
                        'div[class="matchHistoryRow__lostServe matchHistoryRow__green  matchHistoryRow__highlight matchHistoryRow__home"]',
                        'div[class="matchHistoryRow__lostServe matchHistoryRow__green  matchHistoryRow__home"]',
                    )
                ),
                await match_historys[current_round-1].querySelector(
                        (
                        'div[class="matchHistoryRow__lostServe matchHistoryRow__red  matchHistoryRow__highlight matchHistoryRow__away"]',
                        'div[class="matchHistoryRow__lostServe matchHistoryRow__red  matchHistoryRow__highlight matchHistoryRow__home"]',
                        'div[class="matchHistoryRow__lostServe matchHistoryRow__red  matchHistoryRow__away"]',
                        )
                    )
                ]
            except Exception:
                await asyncio.sleep(90)
                continue

            for i in range(1,current_set):
                print("reverse", i)
                result.reverse()
            
            title = await page.title()

            try:
                res = None
                try: res = await page.evaluate('(element) => element.textContent', result[0])
                except Exception: pass
                
                try: res = await page.evaluate('(element) => element.textContent', result[1])
                except Exception: pass

                if res and last_lost != favorite and result[favorite]:
                    last_lost = favorite
                    await bot.send_message(
                        1835953916,
                        f"{title}\n\n{page.url}"
                    )
                try:
                    print(0 if favorite == 1 else 1, result[0 if favorite == 1 else 1], result)
                    if res and result[0 if favorite == 1 else 1]:
                        last_lost = 0 if favorite == 1 else 1
                except Exception: pass

            except Exception as E: print(str(E))
            await asyncio.sleep(90)
            
        await browser.close()