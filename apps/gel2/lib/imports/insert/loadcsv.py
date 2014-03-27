
import csv

from .newlink import NewLink, NewEntry

def load_csv(filepath):
    rows = []
    with open(filepath, "rb") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            rows.append([cell.strip().decode("utf8") for cell in row])

    columns = rows.pop(0)[:]
    new_links = []
    new_entries = []
    for i, row in enumerate(rows):
        if not row or not row[0]:
            # Skip blank rows
            pass
        else:
            entry_data = {col: val for col, val in zip(columns, row)}
            for f, val in entry_data.items():
                if not val.strip():
                    entry_data[f] = None
                else:
                    entry_data[f] = val.strip()
            for f in ("recordID", "alternatives"):
                if f in entry_data and entry_data[f] is not None:
                    try:
                        entry_data[f] = int(entry_data[f])
                    except ValueError:
                        entry_data[f] = None
            if "matched" in entry_data:
                if entry_data["matched"] == "NEW":
                    new_entries.append(NewEntry(entry_data, i))
                elif "recordID" in entry_data and entry_data["recordID"]:
                    new_links.append(NewLink(entry_data, i))

    return (new_links, new_entries)


def update_csv(filepath, new_links, new_entries):
    statuses = {}
    for l in new_links + new_entries:
        statuses[l.row_num] = l.status

    rows = []
    with open(filepath, "rb") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            rows.append(list(row))
    columns = rows.pop(0)[:]

    for i, row in enumerate(rows):
        if i in statuses:
            row[-1] = statuses[i]

    with open(filepath, "wb") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(columns)
        writer.writerows(rows)


def rollback_csv(filepath):
    import re

    rows = []
    with open(filepath, "rb") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            rows.append(list(row))
    columns = rows.pop(0)[:]

    links = []
    entries = []
    for row in [r for r in rows if r and r[-1] is not None and r[-1].strip()]:
        m = re.search(r"ID (\d+)", row[-1])
        if m is not None and row[-1].startswith("link created"):
            links.append(int(m.group(1)))
        elif m is not None and row[-1].startswith("entry created"):
            entries.append(int(m.group(1)))
        row[-1] = "null"

    with open(filepath, "wb") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(columns)
        writer.writerows(rows)

    return (links, entries)
