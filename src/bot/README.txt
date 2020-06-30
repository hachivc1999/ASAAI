****************************************************************************
Mon, Jun 1, 2020 |
-----------------+

How to run:
cd assai_bot
scrapy crawl assai -o [file name].[file extension]
python upload.py

- Where:
	+ [file name]: any name you want, recommend no space
	+ [file extension]: only these extensions are allowed: json, xml, csv

- Cautions:
	+ Please install all these packages first:
		~ pip install scrapy
		~ pip install requests-html
	+ Remember to edit 'upload.py' to upload your file
	according to your [file name]
	+ After finished the 2nd command, you can check the folder 'anime47'
	for details about the run
	+ For more info, try to read these files:
		~ assai_bot/spiders/assai_spiders.py
		~ assai_bot/spiders/util.py
		~ assai_bot/items.py
		~ assai_bot/settings.py

This bot is created with scrapy, you can found all the details at:
https://docs.scrapy.org/en/latest/index.html

****************************************************************************