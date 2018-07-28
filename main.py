import argparse
import render
import story

parser = argparse.ArgumentParser(description='Generate stats for online webfics.')
parser.add_argument('--nothread', dest='nothread', action='store_true',
                    help='scrape in a single thread (default: one thread per story)')
parser.add_argument('--noscrape', dest='noscrape', action='store_true',
                    help='suppress scraping')

args = parser.parse_args()

if not args.noscrape:
    story.handle_stories(not args.nothread)

render.render()
