import os, sys
from PIL import Image, ImageDraw, ImageFont
from google_play_scraper import app
import requests
from io import BytesIO 
from PIL import Image
from webdriver_manager.chrome import ChromeDriverManager
import io #For Reading the Byte File retrieved from selenium

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

import requests
from bs4 import BeautifulSoup

def getFromItchio(url):
	page = requests.get(url)
	soup = BeautifulSoup(page.content, 'html.parser')

	title = soup.find("h1", class_="game_title").text
	description = soup.find("div", class_="formatted_description").text
	screenshots = soup.find_all(".screenshot_list.a")

	link_url = []
	data = soup.findAll('div',class_='screenshot_list')
	for div in data:
		links = div.findAll('a')
		for a in links:
			link_url.append(a['href'])

	return { 'title': title, 'description': description, 'screenshots': link_url}

def merge(im1, im2, im3):
    w = im1.size[0] + im2.size[0] + im3.size[0]
    h = max(im1.size[1], im2.size[1], im3.size[1])
    im = Image.new("RGBA", (w, h))

    im.paste(im1)
    im.paste(im2, (im1.size[0], 0))
    im.paste(im3, (im1.size[0] + im2.size[0], 0))

    return im

def merge2(im1, im2, im3):
    im = Image.new("RGBA", (768, 512))

    im1.thumbnail((768,512))
    im2.thumbnail((768,512))
    im3.thumbnail((768,512))

    im.paste(im1)
    im.paste(im2, (256, 0))
    im.paste(im3, (512, 0))

    return im

def pasteIcon(icon, im):
	icon = icon.resize((128 , 128))
	im.paste(icon, (0, 0))

	return im

def text(img, message):
	font = ImageFont.truetype("Montserrat-Bold.ttf", 64)
	d = ImageDraw.Draw(img)
	d.multiline_text((img.size[0]/2, img.size[1]/2), message, font=font, anchor="ms", fill="white", stroke_width=12, stroke_fill="black")

	return img

def miniature(package, lang, message, output = ''):

	if(output == ''):
		package.replace('.', '').lower() + '_' + lang + '.png'

	result = app(
	    package,
	    lang=lang, # defaults to 'en'
	)

	icon = Image.open(BytesIO(requests.get(result["icon"]).content))
	screen1 = Image.open(BytesIO(requests.get(result["screenshots"][0]).content))
	screen2 = Image.open(BytesIO(requests.get(result["screenshots"][1]).content))
	screen3 = screen2
	
	if(len(result["screenshots"]) > 2):
		screen3 = Image.open(BytesIO(requests.get(result["screenshots"][2]).content))

	# merge screens
	full = merge(screen1, screen2, screen3)
	#full = full.crop((0, 0, 1980, 1080))
	#full = full.resize((256, 256))

	# paste dim
	dim = Image.new("RGBA", (full.size[0], full.size[1]))
	alpha = 0.7
	full = Image.blend(full, dim, alpha)

	# paste icon
	full = pasteIcon(icon, full)

	# paste text
	full = text(full, message)

	full = full.convert('RGB')
	full.save('../' + output, "PNG")

def miniatureFromIch(url, message, output = ''):

	if(output == ''):
		message.replace('\n', '_').replace('!', '').lower() + '.png'

	result = getFromItchio(url)

	#icon = Image.open(BytesIO(requests.get(result["icon"]).content))
	screen1 = Image.open(BytesIO(requests.get(result["screenshots"][0]).content))
	screen2 = Image.open(BytesIO(requests.get(result["screenshots"][1]).content))
	screen3 = Image.open(BytesIO(requests.get(result["screenshots"][2]).content))

	# merge screens
	full = merge2(screen1, screen2, screen3)

	# paste dim
	dim = Image.new("RGBA", (full.size[0], full.size[1]))
	alpha = 0.7
	full = Image.blend(full, dim, alpha)

	# paste text
	full = text(full, message)

	full = full.convert('RGB')
	full.save('../' + output, "PNG")

def miniatureFromWeb(url, message, output = ''):

	if(output == ''):
		message.replace('\n', '_').replace('!', '').lower() + '.png'

	# screen web 
	driver = webdriver.Chrome()
	driver.get(url)
	temp = io.BytesIO(driver.get_screenshot_as_png())
	 
	image = Image.open(temp)

	full = Image.new("RGBA", (768, 512))
	full.paste(image)

	# paste dim
	dim = Image.new("RGBA", (768, 512))
	alpha = 0.7
	full = Image.blend(full, dim, alpha)

	# paste text
	full = text(full, message)

	full = full.convert('RGB')
	full.save('../' + output, "PNG")

def placeholder():
	full = Image.new("RGBA", (768, 512))

	# paste text
	full = text(full, "placeholder")

	full = full.convert('RGB')
	full.save('../placeholder.png', "PNG")

## main
#placeholder()

#miniature('com.poly.france_actu', 'en', 'Actu France\npocket news', 'actufrance.png')
#miniature('com.poly.astrology', 'en', 'Astro\nTarot reading', 'astro.png')
#miniature('com.poly.market', 'fr', 'Bons plans\nEn vrac!', 'envrac.png')
#miniature('com.poly.habit', 'en', 'Habit Frogs!', 'habitfrogs.png')

#miniature('com.clanmo.europcar', 'fr', 'Europcar', 'europcar.png')
#miniature('fr.proximity.proximity', 'fr', 'MyProximity', 'myproximity.png')
#miniature('com.dupuis.webtoonfactory', 'fr', 'Webtoon\nFactory', 'webtoonfactory.png')
##miniature('com.francelive.france', 'fr', 'FranceLive', 'francelive.png')
#miniature('com.beemenergy.mybeem', 'fr', 'Beem Energy', 'beemenergy.png')
#miniature('com.backelite.vingtminutes', 'fr', '20minutes', 'vingtminutes.png')
#miniature('be.rtl.info', 'fr', 'RTL info', 'rtlinfo.png')
#miniature('be.appsolution.lesoir', 'fr', 'Le Soir', 'lesoir.png')
#miniature('fr.k_decole.mobile', 'fr', 'Skolengo', 'skolengo.png')

#miniatureFromIch('https://crucknuk.itch.io/yo-runner', "Yo!\nBox&Boxes", 'yorunner.png')
#miniatureFromIch('https://crucknuk.itch.io/blobi', "Blobitronica", 'blobitronica.png')
#miniatureFromIch('https://crucknuk.itch.io/deepteam', "DeepTeam", 'deepteam.png')

miniatureFromWeb('https://ma-rupture-sentimentale.fr', 'Ma rupture.fr', 'marupture.png')
miniatureFromWeb('https://zenguide.fr', 'ZenGuide.fr', 'zenGuide.png')

print("DONE")
