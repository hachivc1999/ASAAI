# -*- coding: utf-8 -*-

# Define here the models for your scraped items:
# anime = {
#     'name': name,
#     'transName': transName,
#     'producer': producer,
#     'pictureLink': image_link,
#     'tags': tags,
#     'description': description,
#     'seasons': [
#         {
#             'name': name,
#             'releaseDate': release_date,
#             'numberOfEpisode': episode,
#             'isCompleted': isCompleted,
#             'link': response.url,
#         }
#     ]
# }
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class AnimeItem(scrapy.Item):
    # define the fields for anime:
    name = scrapy.Field()
    transName = scrapy.Field()
    producer = scrapy.Field()
    pictureLink = scrapy.Field()
    tags = scrapy.Field()
    description = scrapy.Field()
    seasons = scrapy.Field()


class SeasonsItem(scrapy.Item):
    # define the fields for season:
    name = scrapy.Field()
    releaseDate = scrapy.Field()
    numberOfEpisode = scrapy.Field()
    isCompleted = scrapy.Field()
    link = scrapy.Field()
