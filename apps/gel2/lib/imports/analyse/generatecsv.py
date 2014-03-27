
import csv

headers = ("lemma", "entryID", "nodeID", "wordclass", "definition",
           "matched", "recordID", "recordLabel", "recordDefinition",
           "alternatives", "exitStatus")


def generate_csv(config, entries, outfile):
    with (open(outfile, "wb")) as fh:
        writer = csv.writer(fh)
        writer.writerow(headers)

        for e in entries:
            if e.blocks[0][1] is not None:
                definition = e.blocks[0][1].encode("utf8")
            else:
                definition = None
            row = [e.lemma.encode("utf8"),
                   e.entryid,
                   e.nodeid,
                   e.blocks[0][0],
                   definition,]
            if e.match is not None:
                row.append("MATCHED")
                for k in e.match:
                    if k is not None:
                        row.append(k.encode("utf8"))
                    else:
                        row.append(None)
                row.append(str(e.alternatives))
            else:
                row.append("NEW")
            while len(row) < len(headers):
                row.append(None)
            row[-1] = "null"
            writer.writerow(row)
