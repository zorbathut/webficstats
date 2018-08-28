
from disk import *

import svgwrite
import util_math
import datetime
import os

def render():
    render_wrapper('out_lengths', [render_lengths])
    render_wrapper('out_wpw', [render_words_per_week])
    render_wrapper('out_wpp', [render_words_per_post])
    render_wrapper('out_ppw', [render_posts_per_week])

def render_unified():
    render_wrapper('output', [render_lengths, render_words_per_week, render_words_per_post, render_posts_per_week])

def render_wrapper(filename, funcs):
    width = 800
    cy = 0

    dwg = svgwrite.Drawing(filename=filename + '.svg', debug=True)

    bg = dwg.add(dwg.g())
    fg = dwg.add(dwg.g())

    for func in funcs:
        cy += func(dwg, subgroup(dwg, fg, (0, cy)), width) + 100
    cy -= 100

    textwidth = 150
    imageborder = 20

    ul = (-(textwidth + imageborder), -imageborder - 10)
    br = (width + textwidth + imageborder, cy + imageborder + 10)
    size = (br[0] - ul[0], br[1] - ul[1])

    fg.add(dwg.text('github.com/zorbathut/webficstats',
        insert = (br[0] - 2, br[1] - 2),
        font_family = 'Arial',
        font_size = 10,
        font_style = 'italic',
        text_anchor = 'end',
        alignment_baseline = 'hanging',
        fill_opacity = 0.3 ))

    bg.add(dwg.rect(ul, size, fill='ghostwhite'))

    dwg.viewbox(
        minx = ul[0],
        miny = ul[1],
        width = size[0],
        height = size[1])

    clip_path = dwg.defs.add(dwg.clipPath())
    clip_path.add(dwg.rect(ul, size))

    fg['style'] = f"clip-path: url(#{clip_path.get_iri()});"

    dwg.save()

    os.system(f'inkscape {filename}.svg --export-png {filename}.png --export-dpi 180')

def subgroup(dwg, fg, origin):
    return fg.add(dwg.g(transform = f"translate({origin[0]},{origin[1]})"))

def render_lengths(dwg, g, width):
    data = db()

    sortedstories = sorted((v for (k, v) in data.items()), key = lambda story: story.words_total())
    longestlength = [v for v in sortedstories if v.posterityonly == False][-1].words_total() * 1.05  # little extra just so the graph isn't ending at the exact box edge

    columnheight = 10
    columnborder = 3
    height = columnheight * len(sortedstories)

    g.add(dwg.polyline([(0, 0), (0, columnheight * len(sortedstories)), (width, columnheight * len(sortedstories))], fill = 'none', stroke = 'black', stroke_opacity = 0.5))

    g.add(dwg.text('Total word count',
        insert = (width / 2, -10),
        font_family = 'Arial',
        font_size = 14,
        text_anchor = 'middle',
        alignment_baseline = 'middle',
        fill_opacity = 0.8 ))

    for words in range(0, int(longestlength), 100000):
        if words == 0:
            continue
        if words < 1000000:
            text = str(int(words / 1000)) + 'k'
        else:
            text = str(words / 1000000) + 'm'

        xpos = util_math.remap(0, longestlength, 0, width, words)
        g.add(dwg.line((xpos, 0), (xpos, height), stroke='black', stroke_opacity=0.1, stroke_dasharray="2 4"))
        g.add(dwg.text(text,
            insert = (xpos, height + 10),
            font_family = 'Arial',
            font_size = 8,
            text_anchor = 'middle',
            alignment_baseline = 'hanging',
            fill_opacity = 0.5 ))

        if words == 100000:
            g.add(dwg.text('(standard full-length novel)',
                insert = (xpos, height + 20),
                font_family = 'Arial',
                font_size = 8,
                text_anchor = 'middle',
                alignment_baseline = 'hanging',
                fill_opacity = 0.5 ))

    for idx, story in enumerate(sortedstories):
        start = (0, idx * columnheight + columnborder)
        words = story.words_total()
        size = (words / longestlength * width, columnheight - columnborder * 2)
        g.add(dwg.rect(start, size, fill = story.color))
        if not story.finished:
            gradient = dwg.linearGradient((0, 0), (1, 0))
            gradient.add_stop_color(0, story.color, opacity=0.3)
            gradient.add_stop_color(1, story.color, opacity=0)
            dwg.defs.add(gradient)

            g.add(dwg.rect((start[0] + size[0], start[1] + 1), (20, size[1] - 2), fill = gradient.get_paint_server()))
        g.add(dwg.text(story.name,
            insert = (-5, (idx + 0.8) * columnheight),
            text_anchor = 'end',
            font_family = 'Arial',
            font_size = 10,
            alignment_baseline = 'middle'))
        if words > longestlength:
            g.add(dwg.text(str(round(words / 1000000, 1)) + "m ->",
                insert = (width + 165, (idx) * columnheight),
                text_anchor = 'end',
                font_family = 'Arial',
                font_size = 8,
                fill_opacity = 0.5))

    return height

def render_words_per_week(dwg, g, width):
    data = db()

    weeks = 8

    print(f"Generating words per week . . .")
    storystats = []
    for k, v in [(k, v) for k, v in data.items() if v.dateclass is not None]:
        print("  " + v.name)
        storystats += [(v, v.words_per_week(weeks))]
    print("Completed, rendering")

    return render_standard_chart(
        dwg,
        g,
        width,
        storystats,
        f'Words published per week ({weeks}wk rolling average)',
        render_words_per_week_legend)

def render_words_per_week_legend(dwg, g, width, height, biggeststat):
    #add nanowrimo legends
    for amount, label in [(50000 / 30 * 7, 'nanowrimo'), (50000 / 365 * 7, 'nanowriyr?')]:
        ypos = util_math.remap(0, biggeststat, height, 0, amount)
        g.add(dwg.line((0, ypos), (width, ypos), stroke='black', stroke_opacity=0.15, stroke_dasharray="4 4"))
        g.add(dwg.text(label,
            insert = (-10, ypos + 3),
            font_family = 'Arial',
            font_size = 10,
            font_style = 'italic',
            text_anchor = 'end',
            alignment_baseline = 'middle',
            fill_opacity = 0.7))

    g.add(dwg.text('^ nanowriwk (50k/wk)',
        insert = (-65, -20),
        font_family = 'Arial',
        font_size = 10,
        font_style = 'italic',
        text_anchor = 'start',
        alignment_baseline = 'middle',
        fill_opacity = 0.7))

    for amount, label in [(n * 1000, str(n) + "k/wk") for n in range(0, int(biggeststat / 1000) + 1, 5)]:
        if amount == 0:
            continue
        ypos = util_math.remap(0, biggeststat, height, 0, amount)
        g.add(dwg.line((0, ypos), (width, ypos), stroke='black', stroke_opacity=0.1, stroke_dasharray="2 4"))
        g.add(dwg.text(label,
            insert = (-10, ypos + 3),
            font_family = 'Arial',
            font_size = 8,
            text_anchor = 'end',
            alignment_baseline = 'middle',
            fill_opacity = 0.5))

def render_words_per_post(dwg, g, width):
    data = db()

    weeks = 8

    print(f"Generating words per post . . .")
    storystats = []
    for k, v in [(k, v) for k, v in data.items() if v.dateclass is not None]:
        print("  " + v.name)
        storystats += [(v, v.words_per_post(weeks))]
    print("Completed, rendering")

    return render_standard_chart(
        dwg,
        g,
        width,
        storystats,
        f'Words published per post ({weeks}wk rolling average)',
        render_words_per_post_legend)

def render_words_per_post_legend(dwg, g, width, height, biggeststat):
    for amount, label in [(n, str(n) + " words") for n in range(0, int(biggeststat) + 1, 1000)]:
        if amount == 0:
            continue
        ypos = util_math.remap(0, biggeststat, height, 0, amount)
        g.add(dwg.line((0, ypos), (width, ypos), stroke='black', stroke_opacity=0.1, stroke_dasharray="2 4"))
        g.add(dwg.text(label,
            insert = (-10, ypos + 3),
            font_family = 'Arial',
            font_size = 8,
            text_anchor = 'end',
            alignment_baseline = 'middle',
            fill_opacity = 0.5))

def render_posts_per_week(dwg, g, width):
    data = db()

    weeks = 4

    print(f"Generating posts per week . . .")
    storystats = []
    for k, v in [(k, v) for k, v in data.items() if v.dateclass is not None]:
        print("  " + v.name)
        storystats += [(v, v.posts_per_week(weeks))]
    print("Completed, rendering")

    return render_standard_chart(
        dwg,
        g,
        width,
        storystats,
        f'Posts published per week ({weeks}wk rolling average)',
        render_posts_per_week_legend)

def render_posts_per_week_legend(dwg, g, width, height, biggeststat):
    for amount, label in [(n, str(n) + " posts") for n in range(0, int(biggeststat) + 1, 1)]:
        if amount == 0:
            continue
        ypos = util_math.remap(0, biggeststat, height, 0, amount)
        g.add(dwg.line((0, ypos), (width, ypos), stroke='black', stroke_opacity=0.1, stroke_dasharray="2 4"))
        g.add(dwg.text(label,
            insert = (-10, ypos + 3),
            font_family = 'Arial',
            font_size = 8,
            text_anchor = 'end',
            alignment_baseline = 'middle',
            fill_opacity = 0.5))

def render_standard_chart(dwg, g, width, storystats, title, legend):

    biggeststat = max(max(v[1] for v in data) for story, data in storystats) * 1.1  # little extra just so the graph isn't ending at the exact box edge

    xmin = min(data[0][0] for story, data in storystats)
    xmax = max(data[-1][0] for story, data in storystats)

    height = 300

    textwidth = 150
    imageborder = 20

    ul = (-imageborder - 50, -imageborder - 10)
    br = (width + textwidth + imageborder, height + imageborder)
    size = (br[0] - ul[0], br[1] - ul[1])

    g.add(dwg.polyline([(0, 0), (0, height), (width, height)], fill = 'none', stroke = 'black', stroke_opacity = 0.5))

    g.add(dwg.text(title,
        insert = (width / 2, -10),
        font_family = 'Arial',
        font_size = 14,
        text_anchor = 'middle',
        alignment_baseline = 'middle',
        fill_opacity = 0.8 ))

    if legend is not None:
        legend(dwg, g, width, height, biggeststat)

    for year in range(xmin.year + 1, xmax.year + 1):
        xpos = util_math.remap(xmin, xmax, 0, width, datetime.datetime(year, 1, 1))
        g.add(dwg.line((xpos, 0), (xpos, height), stroke='black', stroke_opacity=0.1, stroke_dasharray="2 4"))
        g.add(dwg.text(str(year),
            insert = (xpos, height + 10),
            font_family = 'Arial',
            font_size = 8,
            text_anchor = 'middle',
            alignment_baseline = 'hanging',
            fill_opacity = 0.5 ))

    print("  Placing lines")
    for story, data in storystats:
        line = []
        for date, amount in data:
            line += [(util_math.remap(xmin, xmax, 0, width, date), util_math.remap(0, biggeststat, height, 0, amount))]
        #g.add(dwg.polyline(line, fill = 'none', stroke = 'ghostwhite', stroke_width = 3)) # for future line standout code
        g.add(dwg.polyline(line, fill = 'none', stroke = story.color))

    print("  Placing unfinished legends")
    endtexts = []
    for story, data in storystats:
        if not story.finished:
            # add it to our list, we'll composite them together later
            endtexts += [(story, int(util_math.remap(0, biggeststat, height, 0, data[-1][1])))]
        else:
            # put it in the middle
            # but bump it up enough that it won't hit the story's line
            wordlen = calctextwidth(story.name, 10)
            wordlendays = util_math.remap(0, width, datetime.timedelta(), xmax - xmin, wordlen).days
            spanstart = int((len(data) - wordlendays) / 2)
            top = max(entry[1] for entry in data[max(spanstart, 0):min(spanstart + wordlendays, len(data))])

            center = data[int(len(data) / 2)]
            g.add(dwg.text(story.name,
                insert = (util_math.remap(xmin, xmax, 0, width, center[0]), util_math.remap(0, biggeststat, height, 0, top) - 10),
                text_anchor = 'middle',
                font_family = 'Arial',
                font_size = 10,
                alignment_baseline = 'baseline',
                stroke = 'ghostwhite',
                stroke_width = 3))
            g.add(dwg.text(story.name,
                insert = (util_math.remap(xmin, xmax, 0, width, center[0]), util_math.remap(0, biggeststat, height, 0, top) - 10),
                text_anchor = 'middle',
                font_family = 'Arial',
                font_size = 10,
                alignment_baseline = 'baseline',
                fill = story.color))

    print("  Placing finished legends")
    cyclesremaining = 1000
    while cyclesremaining > 0:
        cyclesremaining = cyclesremaining - 1

        bumped = False

        bumppos = {}
        bumpneg = {}

        for source, sposition in endtexts:
            for target, eposition in endtexts:
                if source == target:
                    continue

                if abs(eposition - sposition) < 10:
                    bumped = True
                    if eposition < sposition:
                        bumppos[source] = True
                    elif sposition < eposition:
                        bumpneg[source] = True
                    elif source.name < target.name:
                        bumppos[source] = True
                    else:
                        bumpneg[source] = True

        if not bumped:
            break

        for index in range(len(endtexts)):
            if endtexts[index][0] in bumppos:
                endtexts[index] = (endtexts[index][0], endtexts[index][1] + 1)
            if endtexts[index][0] in bumpneg:
                endtexts[index] = (endtexts[index][0], endtexts[index][1] - 1)

    if cyclesremaining == 0:
        print(f"  Rearrangement complete with {cyclesremaining} remaining")

    for story, position in endtexts:
        g.add(dwg.text(story.name,
            insert = (width + 5, position),
            text_anchor = 'start',
            font_family = 'Arial',
            font_size = 10,
            alignment_baseline = 'middle',
            fill = story.color))

    return height

def calctextwidth(text, fontsize=14):
    import cairo

    surface = cairo.SVGSurface('undefined.svg', 1280, 200)
    cr = cairo.Context(surface)
    cr.select_font_face('Arial', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    cr.set_font_size(fontsize)
    xbearing, ybearing, width, height, xadvance, yadvance = cr.text_extents(text)
    return width
