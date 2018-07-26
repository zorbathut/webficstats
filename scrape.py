
from story import *
from disk import *

import svgwrite

#handle_stories()

data = db()

sortedstories = sorted((v for (k, v) in data.items()), key = lambda story: story.words_total())
longestlength = sortedstories[-1].words_total() * 1.03  # little extra just so the graph isn't ending at the exact box edge

width = 800
columnheight = 10
columnborder = 3

textwidth = 100
imageborder = 20

ul = (-(textwidth + imageborder), -imageborder)
br = (width + imageborder, columnheight * len(sortedstories) + imageborder)
size = (br[0] - ul[0], br[1] - ul[1])

dwg = svgwrite.Drawing(filename='quantity.svg', debug=True)
dwg.viewbox(
    minx = ul[0],
    miny = ul[1],
    width = size[0],
    height = size[1])
dwg.add(dwg.rect(ul, size, fill='ghostwhite'))
dwg.add(dwg.polyline([(0, 0), (0, columnheight * len(sortedstories)), (width, columnheight * len(sortedstories))], fill = 'none', stroke = 'black'))
for idx, story in enumerate(sortedstories):
    dwg.add(dwg.rect((0, idx * columnheight + columnborder), (story.words_total() / longestlength * width, columnheight - columnborder * 2)))
    dwg.add(dwg.text(story.name, insert = (-5, (idx + 0.8) * columnheight), text_anchor = 'end', font_size = 10, alignment_baseline = 'middle'))
dwg.save()
