# Extracts all the tracks, chapters, tags and fonts
from pathlib import Path
import re
import subprocess
import pymkv

current_directory = (Path.cwd()).resolve()
output_directory = (current_directory / 'output').resolve()

def create_folder():
	'''Creates the output folder if it doesn't already exist'''

	if not output_directory.exists():
		output_directory.mkdir()
		

def extract_fonts(mkvfile):
	'''Extracts the fonts from the mkvfile'''

	fonts = []
	fonts_command = ''

	mkvinfo = subprocess.run('mkvmerge --identify \"{}\"'.format(mkvfile), capture_output=True, text=True, shell=True)
	pattern = re.compile(r'name \'.+(.ttf|.otf|.TTF|.OTF)\'')
	matches = pattern.finditer(mkvinfo.stdout)

	for match in matches:
		fonts.append(mkvinfo.stdout[match.start() + 6 : match.end() - 1])

	attachment_folder = (output_directory / mkvfile.name).resolve()
	font_folder = (attachment_folder / 'attachments').resolve()
	
	if not attachment_folder.exists():		
		attachment_folder.mkdir()
		font_folder.mkdir()

	for i, font in enumerate(fonts, 1):
		fonts_command += '{}:\"{}\" '.format(i, font_folder / font)
	
	if fonts_command != '':
		subprocess.run('mkvextract \"{}\" attachments {}'.format(mkvfile, fonts_command), shell=True)
	else:
		print('No fonts\n')


def extract_subs(mkvfile):
	'''Extracts the subs from the mkvfile'''

	mkv = pymkv.MKVFile(mkvfile)
	tracks = mkv.get_track()

	subtitle_command = ''

	for track in tracks:
		if track.track_type == 'subtitles':
			subtitle_command += '{}:\"{}/track{}_{}.ass\" '.format(track.track_id, output_directory / mkvfile.name, track.track_id + 1,  track.language)

	if subtitle_command != '':
		subprocess.run('mkvextract \"{}\" tracks {}'.format(mkvfile, subtitle_command), shell=True)
	else:
		print('No subtitles\n')


def extract_chapters(mkvfile):
	'''Extracts the chapter from the mkvfile'''

	subprocess.run('mkvextract \"{}\" chapters \"{}\"'.format(mkvfile, output_directory / mkvfile.name / 'chapters.xml'), shell=True)


def main():
	create_folder()
	mkvfiles = sorted([item for item in current_directory.iterdir() if item.suffix == '.mkv'])

	if mkvfiles:
		for mkvfile in mkvfiles:
			print('Working File: ', mkvfile.name, end='\n\n')

			print('\nExtracting Fonts:\n')
			extract_fonts(mkvfile)

			print('\nExtracting Chapters:\n')
			extract_chapters(mkvfile)

			print('\nExtracting Subs:\n')
			extract_subs(mkvfile)

			print("\n")


if __name__ == '__main__':
	main()