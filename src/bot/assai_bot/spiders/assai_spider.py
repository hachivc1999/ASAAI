import scrapy
import time
from requests_html import HTMLSession, HTML

from .util import *
from ..items import AnimeItem, SeasonsItem

anime47_dict = {
    ' TV': '', ' Bluray': '', ' Blu-ray': '', ' (Blu-ray)': '', ' [BD]': '',
    ' BD': '', ' [Blu-ray]': '', ' (Blu-ray )': '', ' Bd': '', ' ONA': ' (ONA)',
    ' [SS1]': '', ' SS1': '',
    ' ~': ' Movie: ',
    'Ψ Nan': 'Ψ-nan',
    'Ψ-nan: Shidou-hen': 'Ψ-nan: Ψ-shidou-hen',
    'Date A Live Season 2': 'Date A Live II',
    'Date A Live: Encore OVA': 'Date A Live: Encore',
    ' (Tháng tư là lời nói dối của em)': '',
    'Shigatsu wa Kimi no Uso (OVA)': 'Shigatsu wa Kimi no Uso: Moments',
    'Vua bếp Soma - ': '',
    'Date A Live Ⅲ': 'Date A Live III',
    ': Mayuri Judgement': ' Movie: Mayuri Judgment',
    'San no Sara - Toutsuki Ressha-hen': 'San no Sara - Tootsuki Ressha-hen',
    'Đại Chiến Underworld': 'War of Underworld',
    'Kobayashi-san Chi no Maid Dragon OVA': 'Kobayashi-san Chi no Maid Dragon: Valentine, Soshite Onsen! - Amari Kitai Shinaide Kudasai',
    'Himouto! Umaru-chan S': 'Himouto! Umaru-chanS',
    'Beck Mongolian Chop Squad': 'Beck',
    'Alice or Alice: Siscon Niisan to Futago no Imouto': 'Alice or Alice',
    'Gochuumon Wa Usagi Desu Ka [SS2]': 'Gochuumon Wa Usagi Desu Ka??',
    'Seitokai Yakuindomo 2': 'Seitokai Yakuindomo*',
    'Amanchu! Special': 'Amanchu!: Upyopyo Dive Tsukkome! Umi no Sekai!',
    'Karakai Jouzu no Takagi-san OVA': 'Karakai Jouzu no Takagi-san: Water Slide',
    'Chuunibyou Demo Koi Ga Shitai! Specials - Depth Of Field - Ai To Nikushimi Gekijou': 'Chuunibyou demo Koi ga Shitai!: Depth of Field - Ai to Nikushimi Gekijou',
    'Chuunibyou Demo Koi Ga Shitai! Ren SS2': 'Chuunibyou Demo Koi Ga Shitai! Ren',
    'Chuunibyou Demo Koi Ga Shitai! Ova': 'Chuunibyou demo Koi ga Shitai!: Kirameki no... Slapstick Noel',
    'One Room 2nd Season': 'One Room Second Season',
    'One Room 2nd Season Special': 'One Room Second Season Special',
    'White Album Season 1': 'White Album',
    'Grisaia Phantom Trigger': 'Grisaia Phantom Trigger - The Animation',
    'Hitoribocchi no ○○ Seikatsu': 'Hitoribocchi no Marumaru Seikatsu',
    'Gochuumon wa Usagi Desuka??: Sing for You': 'Gochuumon wa Usagi Desu ka??: Sing for You',
    'Kiratto Pri☆chan 2nd Season': 'Kiratto Pri☆chan Season 2',
    'Chihayafuru 2: Waga Mi Yo Ni Furu Nagame Seshi Ma Ni': 'Chihayafuru 2: Waga Miyo ni Furu Nagame Shima ni',
    'Chihayafuru SS1': 'Chihayafuru',
    'Chihayafuru SS2': 'Chihayafuru 2',
    'Yuru Yuri ♪♪ [SS2]': 'Yuru Yuri♪♪',
    'Heya Camp△: Sauna to Gohan to Miwa Bike': 'Heya Camp△: Sauna to Gohan to Sanrin Bike',
    'Non Non Biyori Repeat OVA': 'Non Non Biyori Repeat: Hotaru ga Tanoshinda',
    'Non Non Biyori OAD': 'Non Non Biyori: Okinawa e Ikukoto ni Natta',
    'Osomatsu-san 2': 'Osomatsu-san 2nd Season',
    'Nichijou OVA': 'Nichijou: Nichijou no 0-wa',
    'Mitsuwano OVA': 'Mitsuwano',
    'Girlfriend (Kari) - Bạn Gái (Tạm Thời)': 'Girlfriend (Kari)',
    'Momokuri (TV)': 'Momokuri',
    'Yahari Ore No Seishun Love Come Wa Machigatteiru': 'Yahari Ore no Seishun Love Comedy wa Machigatteiru.',
    'Papa No Iukoto Wo Kikinasai OVA': 'Papa No Iukoto Wo Kikinasai! OVA',
    'Classroom Crisis': 'Classroom☆Crisis',
    'Aria the Origination Special': 'Aria the Origination: Sono Choppiri Himitsu no Basho ni...',
    'Grisaia Phantom Trigger - The Animation': 'Grisaia: Phantom Trigger - The Animation',
    'Room Mate: One Room Side M': 'Room Mate',
    'Crayon Shin-chan Movie 23: Ora no Hikkoshi Monogatari Saboten Dai Shugeki': 'Crayon Shin-chan Movie 23: Ora no Hikkoshi Monogatari - Saboten Daisuugeki',
    'Kyoukai no Kanata Episode 0: Shinonome': 'Kyoukai no Kanata: Shinonome',
    'Kyoukai no Kanata Movie: I\'ll Be Here - Kako-hen': 'Kyoukai no Kanata Movie 1: I\'ll Be Here - Kako-hen',
    'Kyoukai no Kanata Movie: I\'ll Be Here - Mirai-hen': 'Kyoukai no Kanata Movie 2: I\'ll Be Here - Mirai-hen',
    'Miss Monochrome:': 'Miss Monochrome'
}

myanimelist_dict = {
    'Synonyms: ': '',
    'English: ': '',
    'Japanese: ': '',
    'Mayuri Judgment': 'Mayuri Judgement',
    'Food Wars! Shokugeki no Soma OVA': 'Shokugeki no Soma OVA',
    'San no Sara - Tootsuki Ressha-hen': 'San no Sara - Toutsuki Ressha-hen',
    'Himouto! Umaru-chanS': 'Himouto! Umaru-chan S',
    'Yuru Yuri♪♪': 'Yuru Yuri ♪♪'
}

tags_dict = {
    'Hài Hước': 'Comedy', 'Đời Thường': 'Slice of life', 'Phiêu Lưu': 'Adventure',
    'Lịch Sử': 'Historical', 'Trinh Thám': 'Dectective', 'Kinh Dị': 'Horror',
    'Học Đường': 'School', 'Siêu Nhiên': 'Supernatural', 'Thể Thao': 'Sports',
    'Hành Động': 'Action', 'Âm Nhạc': 'Music', 'Phép Thuật': 'Magic',
    'Viễn Tưởng': 'Sci-Fi'
}

seasons_dict = {'Mùa Xuân ': "Spring ", "Mùa Hạ ": "Summer ", "Mùa Thu ": "Autumn ", "Mùa Đông ": "Winter "}


def isMismatch(name, title):
    if not name or not title:
        return True
    return name.lower() != title.lower()


def anime47_parser(name):
    for key in anime47_dict:
        if key in name:
            name = name.replace(key, anime47_dict[key])

    return name


def myanimelist_parser(name):
    for key in myanimelist_dict:
        if key in name:
            name = name.replace(key, myanimelist_dict[key])

    return name


def tags_parser(tags: list):
    if 'Blu-ray' in tags:
        tags.remove('Blu-ray')
    for i in range(len(tags)):
        tag = tags[i]
        if tag in tags_dict:
            tags[i] = tags_dict.get(tag)

    return tags


def date_parser(date: str, season: str):
    release_date = ''
    if date == 'Đang cập nhật':
        release_date = 'Updating'
    elif season and date:
        for key in seasons_dict:
            if key in season:
                release_date += seasons_dict[key]
        release_date += date
    elif date:
        release_date = date
    else:
        release_date = 'Updating'
    return release_date


def anime_url_search(name: str, l_transName: list, search_result: list):
    if not search_result:
        return name, ''

    list_transName = [transName.lower() for transName in l_transName]

    for search in search_result:
        title = search.text
        anime_url = search.attrs.get('href')
        if title.lower() == name.lower():
            # print("Here 1")
            return name, anime_url

        if title.lower() in list_transName:
            # print("Here 2")
            return title, anime_url

        synonyms_list = ''
        time.sleep(1)
        html = HTML(html=HTMLSession().get(anime_url).content)
        results = html.find('.borderClass div .spaceit_pad')
        for result in results:
            synonyms_list += result.text + ', '
        synonyms_list = myanimelist_parser(synonyms_list)
        synonyms_list = synonyms_list.split(', ')
        # print("List of synonyms: ", synonyms_list)
        for synonym in synonyms_list:
            if synonym.lower() == name.lower():
                # print("Here 3")
                return title, anime_url
            if synonym.lower() in list_transName:
                # print("Here 4")
                return title, anime_url

    return name, ''


class AssAI(scrapy.Spider):
    name = 'assai'
    base_url = 'https://anime47.com'
    # TODO: search_url = 'https://myanimelist.net/anime.php?q='
    search_url = 'https://myanimelist.net/search/all?q='
    start_urls = [
        # 'https://anime47.com/the-loai/hai-huoc-24/1.html'
        # 'https://anime47.com/the-loai/blu-ray-46/1.html'
        'https://anime47.com/the-loai/doi-thuong-38/1.html'
        # 'https://anime47.com/the-loai/ecchi-25/1.html'
    ]

    page_number = 1
    last_page = 0

    directory = 'anime47'
    crawled_file = directory + '/crawled.txt'
    cant_crawl_file = directory + '/cant.txt'
    crawled = set()
    cant_crawl = set()

    def reload_data(self):
        create_project_dir(self.directory)
        create_data_file(self.crawled_file)
        create_data_file(self.cant_crawl_file)
        self.crawled = file_to_set(self.crawled_file)
        self.cant_crawl = file_to_set(self.cant_crawl_file)

    def isCrawled(self, link):
        if link not in self.crawled:
            return False
        return True

    def cache(self, link):
        self.crawled.add(link)
        set_to_file(self.crawled, self.crawled_file)

    def update_cant_crawl(self, link):
        self.cant_crawl.add(link)
        set_to_file(self.cant_crawl, self.cant_crawl_file)

    def parse(self, response):
        """ Loop through the main page to look for anime links """
        ## Load previous run for not recrawling pages
        self.reload_data()
        self.cache(response.url)
        for anime_block in response.css('.movie-item.m-block'):
            anime_link = anime_block.css('a::attr(href)').extract()[0]
            anime_link = response.urljoin(anime_link)
            if not self.isCrawled(anime_link):
                yield scrapy.Request(anime_link, callback=self.parse_anime)

        """ Move to the next page """
        page_link = response.css('.pagination-lg a::attr(href)').extract()[-1]
        max_page = int(page_link.split('/')[-1].replace('.html', ''))
        self.last_page = max_page if max_page > self.last_page else self.last_page

        if self.page_number % 5 == 0:
            print("\n#################################################################################################")
            print("Report: ",end="##################################################################################\n")
            print("Current page: ", self.page_number)
            print("Crawled: " + str(len(self.crawled)) + " | Can't crawl: " + str(len(self.cant_crawl)))
            print("#################################################################################################\n")
            time.sleep(5)
        self.page_number += 1
        if self.page_number <= self.last_page:
            url = response.url.replace(str(self.page_number - 1) + '.html', str(self.page_number) + '.html')
            if not self.isCrawled(url):
                yield scrapy.Request(url, callback=self.parse)

    def parse_anime(self, response):
        season_table = response.css('table tr td a::attr(href)').extract()
        if season_table:
            l_anime = []
            l_season = []
            for season in season_table:
                url = response.urljoin(season)
                if not self.isCrawled(url):
                    self.cache(url)
                    anime, anime_seasons = self.crawl_season(url)
                    if anime:
                        l_anime += [anime]
                        l_season += anime_seasons
                    else:
                        self.update_cant_crawl(url)
                        print("In parse anime - Can't crawl season: ", url,
                              end=' |-------------------------------------------------------------------------------\n')
            if l_anime:
                for anime in l_anime:
                    anime['seasons'] = l_season
                    yield anime
            else:
                self.update_cant_crawl(response.url)
                print("In parse anime - Can't crawl seasons: ", response.url,
                      end=' |-------------------------------------------------------------------------------------\n')
        else:
            self.cache(response.url)
            anime = AssAI.crawl_anime(response)
            if anime:
                yield anime
            else:
                self.update_cant_crawl(response.url)
                print("In parse anime - Can't crawl anime: ", response.url,
                      end=' |---------------------------------------------------------------------------------\n')

    @staticmethod
    def crawl_anime(response):  # This method works with the response object from scrapy
        if response.css('.imdb::text').extract()[0] == 'PV':
            return None

        """ Crawl the anime's name and transName for search """
        name = response.css('.title-1::text').extract()[0]
        if 'live action' in name.lower():
            return None
        name = anime47_parser(name)

        l_transName = response.css('.title-2::text').extract()
        l_transName = l_transName[0] if l_transName else ''
        if l_transName:
            if 'live action' in l_transName.lower():
                return None
            if ' | ' in l_transName:
                l_transName = l_transName.split(' | ')
            else:  # Ensure that, type(l_transName) is list
                l_transName = [l_transName]

            l_transName = [anime47_parser(transName) for transName in l_transName]
        else:
            l_transName = []

        """ Crawl the anime's image link """
        image_link = response.css('.movie-l-img img::attr(src)').extract()[0]

        """ Crawl and reformat the anime' tags """
        tags = response.css('.dd-cat a::text').extract()
        tags = tags_parser(tags)

        """ Crawl and reformat the anime's release date """
        season = response.css('.movie-dd:nth-child(11) a::text').extract()
        season = season[0] if season else ''
        date = response.css('.movie-dd:nth-child(14) a::text').extract()
        date = date[0] if date else ''

        release_date = date_parser(date, season)

        """ Crawl some data on myanimelist.net """
        keyword = name.replace(' ', '%20')
        myanimelist_search = AssAI.search_url + str(keyword)
        time.sleep(1)
        search_result = HTML(html=HTMLSession().get(myanimelist_search).content).find(
            '.information.di-tc.va-t.pt4.pl8 a', containing=name)
        search_result.sort(key=lambda x: x.text)

        name, anime_url = anime_url_search(name, l_transName, search_result)

        if not anime_url:
            if not l_transName:
                print("In crawl anime - Can't crawl: ", name, end=" |*******************************************************\n")
                return None
            for transName in l_transName:
                keyword = transName.replace(' ', '%20')
                myanimelist_search = AssAI.search_url + str(keyword)
                time.sleep(1)
                search_result = HTML(html=HTMLSession().get(myanimelist_search).content).find(
                    '.information.di-tc.va-t.pt4.pl8 a')
                name, anime_url = anime_url_search(name, l_transName, search_result)
                if anime_url:
                    break

        if not anime_url:
            print("In crawl anime - Can't crawl: ", name + ' or ', end="")
            print(l_transName, end=" |*******************************************************\n")
            return None

        time.sleep(1)
        html = HTML(html=HTMLSession().get(anime_url).content)

        """ Crawl the anime's description """
        description = html.find('h2+ span', first=True)
        description = description.text if description else ''

        """ Crawl and reformat the anime's transName if it's None """
        transName = html.find('h2+ .spaceit_pad', first=True)
        transName = transName.text if transName else ''

        """ Crawl the producer, anime status and the number of episodes of the anime """
        producer = episode = status = ''
        for e in html.find('div'):
            if e.find('span.dark_text', containing='Producers'):
                producer = e.text.replace('Producers: ', '')
            if e.find('span.dark_text', containing='Episodes'):
                episode = e.text.replace('Episodes: ', '')
            if e.find('span.dark_text', containing='Status'):
                status = e.text.replace('Status: ', '')

        anime = AnimeItem()
        anime_seasons = SeasonsItem()

        anime_seasons['releaseDate'] = release_date
        anime_seasons['numberOfEpisode'] = 0 if episode == 'Unknown' else int(episode)
        anime_seasons['isCompleted'] = 1 if 'Finished' in status else 0
        anime_seasons['link'] = response.url
        anime_seasons['name'] = anime['name'] = myanimelist_parser(name)
        anime['transName'] = myanimelist_parser(transName)
        anime['producer'] = '' if producer == 'None found, add some' else producer
        anime['pictureLink'] = image_link
        anime['tags'] = tags
        anime['description'] = description
        anime['seasons'] = [anime_seasons]

        return anime

    @staticmethod
    def crawl_season(url):  # This method works with the url: str
        html = HTML(html=HTMLSession().get(url).content)
        if html.find('.imdb', first=True).text == 'PV':
            return None, None

        """ Crawl the anime's name and transName """
        name = html.find('.title-1', first=True).text
        if 'live action' in name.lower():
            return None, None
        name = anime47_parser(name)

        l_transName = html.find('.title-2', first=True).text
        if l_transName:
            if 'live action' in l_transName.lower():
                return None, None
            if ' | ' in l_transName:
                l_transName = l_transName.split(' | ')
            else:  # Ensure that, type(l_transName) is list
                l_transName = [l_transName]

            l_transName = [anime47_parser(transName) for transName in l_transName]
        else:
            l_transName = []

        """ Crawl the anime's image link """
        image_link = html.find('.movie-l-img img', first=True).attrs.get('src')

        """ Crawl and reformat the anime' tags """
        tags = html.find('.movie-dd.dd-cat', first=True).text
        tags = tags.split(', ')
        tags = tags_parser(tags)

        """ Crawl and reformat the anime's release date """
        season = html.find('.movie-dd:nth-child(11) a', first=True)
        season = season.text if season else ''
        date = html.find('.movie-dd:nth-child(14) a', first=True)
        date = date.text if date else ''

        release_date = date_parser(date, season)

        """ Crawl some data on myanimelist.net """
        keyword = name.replace(' ', '%20')
        myanimelist_search = AssAI.search_url + str(keyword)
        time.sleep(1)
        search_result = HTML(html=HTMLSession().get(myanimelist_search).content).find(
            '.information.di-tc.va-t.pt4.pl8 a', containing=name)
        search_result.sort(key=lambda x: x.text)

        name, anime_url = anime_url_search(name, l_transName, search_result)

        if not anime_url:
            if not l_transName:
                print("In crawl anime - Can't crawl: ", name, end=" |*******************************************************\n")
                return None, None
            for transName in l_transName:
                keyword = transName.replace(' ', '%20')
                myanimelist_search = AssAI.search_url + str(keyword)
                time.sleep(1)
                search_result = HTML(html=HTMLSession().get(myanimelist_search).content).find(
                    '.information.di-tc.va-t.pt4.pl8 a')
                name, anime_url = anime_url_search(name, l_transName, search_result)
                if anime_url:
                    break

        if not anime_url:
            print("In crawl anime - Can't crawl: ", name + ' or ', end="")
            print(l_transName, end=" |*******************************************************\n")
            return None, None

        time.sleep(1)
        html = HTML(html=HTMLSession().get(anime_url).content)

        """ Crawl the anime's description """
        description = html.find('h2+ span', first=True)
        description = description.text if description else ''

        """ Crawl and reformat the anime's transName if it's None """
        transName = html.find('h2+ .spaceit_pad', first=True)
        transName = transName.text if transName else ''

        """ Crawl the producer, anime status and the number of episodes of the anime """
        producer = episode = status = ''
        for e in html.find('div'):
            if e.find('span.dark_text', containing='Producers'):
                producer = e.text.replace('Producers: ', '')
            if e.find('span.dark_text', containing='Episodes'):
                episode = e.text.replace('Episodes: ', '')
            if e.find('span.dark_text', containing='Status'):
                status = e.text.replace('Status: ', '')

        anime = AnimeItem()
        anime_seasons = SeasonsItem()

        anime['name'] = anime_seasons['name'] = myanimelist_parser(name)
        anime['transName'] = myanimelist_parser(transName)
        anime['producer'] = '' if producer == 'None found, add some' else producer
        anime['pictureLink'] = image_link
        anime['tags'] = tags
        anime['description'] = description
        anime_seasons['releaseDate'] = release_date
        anime_seasons['numberOfEpisode'] = 0 if episode == 'Unknown' else int(episode)
        anime_seasons['isCompleted'] = 1 if 'Finished' in status else 0
        anime_seasons['link'] = url

        return anime, [anime_seasons]
