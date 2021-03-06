import argparse
import render
import story
import disk

parser = argparse.ArgumentParser(description='Generate stats for online webfics.')
parser.add_argument('--nothread', dest='nothread', action='store_true',
                    help='scrape in a single thread (default: one thread per story)')
parser.add_argument('--noscrape', dest='noscrape', action='store_true',
                    help='suppress scraping')
parser.add_argument('--unified', dest='unified', action='store_true',
                    help='output a single image')

args, unknownargs = parser.parse_known_args()

if len(unknownargs) > 0:
    story.handle_story(unknownargs[0])
    disk.save_cache()
elif not args.noscrape:
    story.handle_stories(not args.nothread)

if args.unified:
    render.render_unified();
else:
    render.render()
