#-------------------------------------------------------------------------------
# Name: FileParser
# Purpose:
#
# Author: James McCracken
#-------------------------------------------------------------------------------

from lxml import etree

from .posmap import PosMap
from .dictentry import DictEntry

parser = etree.XMLParser(remove_blank_text=True)

class FileParser(object):

    def __init__(self, config):
        self.config = config
        self.namespaces = {k: v for k, v in config.items("namespaces")}
        self.hw_placeholder = config.get("xpathSubentry", "headwordPlaceholder")
        self.posmap = PosMap(config)

    def parse(self, filelikes):
        self.entries = []
        for f in filelikes:
            root = etree.parse(f).find(".")
            for entry_type in ("regular", "compound"):
                if entry_type == "regular":
                    entry_xpath = self.config.get("xpathEntry", "entry")
                else:
                    entry_xpath = self.config.get("xpathEntry", "compoundEntry")
                for entry in self._xpath(root, entry_xpath):
                    self._parse_entry(entry, entry_type)

    def _parse_entry(self, entry, entry_type):
        id = self._xpath_text(entry, self.config.get("xpathEntry", "id"))
        headword = self._xpath_text(entry, self.config.get("xpathEntry", "headword"))
        blocks = self._parse_wordclass_blocks(entry, "entry", headword)
        if entry_type != "compound":
            self.entries.append(DictEntry(id, None, headword, blocks))
        self._parse_subentries(id, headword, entry)

    def _parse_subentries(self, id, headword, entry):
        subentries = self._xpath(entry, self.config.get("xpathSubentry", "subentry"))
        for subentry in subentries:
            nodeid = self._xpath_text(subentry, self.config.get("xpathSubentry", "id"))
            lemma_node = self._xpath_first(subentry, self.config.get("xpathSubentry", "lemma"))
            lemma = self._lemma_text(lemma_node, headword)
            blocks = self._parse_wordclass_blocks(subentry, "subentry", lemma)
            self.entries.append(DictEntry(id, nodeid, lemma, blocks))

    def _parse_wordclass_blocks(self, node, node_type, lemma):
        config_section = "xpath" + node_type.capitalize()

        blocks = []
        if self.config.get(config_section, "wordclassBlock"):
            blocks = self._xpath(node, self.config.get(config_section, "wordclassBlock"))
        if not blocks:
            blocks = [node,]

        parsed_blocks = []
        for block in blocks:
            definition = self._xpath_text(block, self.config.get(config_section, "definition"))
            if definition is not None:
                definition = definition[0:100]
            parts = self._xpath(block, self.config.get(config_section, "pos"))
            if parts:
                try:
                    parts[0].lower()
                except AttributeError:
                    parts = [self._xpath_text(n, ".") for n in parts]
            else:
                parts = [self._default_pos(lemma),]
            parts = [self.posmap.convert(p) for p in parts]
            for wordclass in parts:
                if not wordclass in [b[0] for b in parsed_blocks]:
                    parsed_blocks.append((wordclass, definition,))

        return parsed_blocks

    def _default_pos(self, lemma):
        if self._is_capitalized(lemma):
            return self.config.get("characteristics", "defaultPosCapitalized")
        else:
            return self.config.get("characteristics", "defaultPosUncapitalized")

    def _xpath_first(self, node, expression):
        try:
            return self._xpath(node, expression)[0]
        except IndexError:
            return None

    def _xpath_text(self, node, expression):
        n = self._xpath_first(node, expression)
        if n is not None:
            # n may be a node or a string-like, depending on whether the
            #   Xpath selector was for an element, an attribute, or a text node
            try:
                n.lower()
            except AttributeError:
                return etree.tostring(n, method="text", encoding=unicode)
            else:
                return unicode(n)
        else:
            return None

    def _xpath(self, node, expression):
        if expression is None or not expression.strip():
            return []
        else:
            try:
                return node.xpath(expression.strip(),
                                  namespaces=self.namespaces)
            except etree.XPathEvalError:
                return []

    def _lemma_text(self, lemma_node, headword):
        if lemma_node is not None:
            # Replace <rf/>-style placeholder with the entry headword
            if self.hw_placeholder:
                placeholder = lemma_node.find(self.hw_placeholder)
                if placeholder is not None and placeholder.text is None:
                    if headword and placeholder.tail:
                        placeholder.tail = headword + placeholder.tail
                    elif headword:
                        placeholder.tail = headword
            return etree.tostring(lemma_node, method="text", encoding=unicode)
        else:
            return None

    def _is_capitalized(self, lemma):
        if lemma is not None and lemma and lemma[0] == lemma[0].capitalize():
            return True
        else:
            return False


