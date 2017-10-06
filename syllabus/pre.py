"""
Pre-process a syllabus (class schedule) file. 

"""
import arrow   # Dates and times
import logging
logging.basicConfig(format='%(levelname)s:%(message)s',
                    level=logging.INFO)
log = logging.getLogger(__name__)

base = arrow.now()   # Default, replaced if file has 'begin: ...'

current_time = arrow.get()

def process(raw):
    """
    Line by line processing of syllabus file.  Each line that needs
    processing is preceded by 'head: ' for some string 'head'.  Lines
    may be continued if they don't contain ':'.  If # is the first
    non-blank character on a line, it is a comment ad skipped. 
    """
    field = None
    entry = {}
    cooked = []
    current_week = 1
    t_f = 0
    for line in raw:
        log.debug("Line: {}".format(line))
        line = line.strip()
        if len(line) == 0 or line[0] == "#":
            log.debug("Skipping")
            continue
        parts = line.split(':')
        if len(parts) == 1 and field:
            entry[field] = entry[field] + line + " "
            continue
        if len(parts) == 2:
            field = parts[0]
            # content is the next str after :
            content = parts[1]
        else:
            raise ValueError("Trouble with line: '{}'\n".format(line) +
                             "Split into |{}|".format("|".join(parts)))

        if field == "begin":
            try:
                # base is date at top of schedule.txt in proper format
                base = arrow.get(content, "MM/DD/YYYY")
                base_plus = base.shift(weeks=+1)
                # print("Base date {}".format(base.isoformat()))
            except:
                raise ValueError("Unable to parse date {}".format(content))

        # Check if we are in the week column
        elif field == "week":
            if entry:
                cooked.append(entry)
                entry = {}
                # Check if the computer's current time is in the week
                # we are about to display.
                if base <= current_time <= base_plus:
                    t_f = 1
                else:
                    t_f = 0
            # Entries for the html file to handle
            entry['date'] = base
            entry['current'] = t_f
            entry['topic'] = ""
            entry['project'] = ""
            entry['week'] = content
            current_week += 1
            # Shift the weeks by one into the future
            base = base.shift(weeks=+1)
            base_plus = base_plus.shift(weeks=+1)

        elif field == 'topic' or field == 'project':
            entry[field] = content

        else:
            raise ValueError("Syntax error in line: {}".format(line))

    if entry:
        cooked.append(entry)

    return cooked


def main():
    f = open("data/schedule.txt")
    parsed = process(f)
    print(parsed)


if __name__ == "__main__":
    main()
