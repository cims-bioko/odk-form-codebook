#!/usr/bin/env python3

##
# Generates a code book for selection-type questions from an ODK xform definition
##

import lxml.etree as etree
import re
import argparse

argp = argparse.ArgumentParser()
argp.add_argument('--lang', help='use LANG translation for form')
argp.add_argument('xform', help='path to the ODK xform definition')
args = argp.parse_args()

NSMAP = {'xf':'http://www.w3.org/2002/xforms'}

try:
    tree = etree.parse(args.xform)
except OSError as e:
    argp.exit(1, "%s\n" % e)

def label_value(elem):
    v = elem.find('xf:value', namespaces=NSMAP)
    head = v.text or ''
    def to_str(o):
        return etree.tostring(o, encoding=str)
    def flatten(o):
        if hasattr(o, 'tag') and o.tag == "{%s}output" % NSMAP['xf']:
            return '{%s}' % o.attrib['value'] + (o.tail or '')
        return to_str(o)
    tail = ''.join(map(flatten, v))
    return head + tail

def find_labels(lang=None):
    if not lang is None:
        lang_trans_path = '//xf:translation[@lang=\'%s\']/xf:text' % lang
        lang_trans = tree.xpath(lang_trans_path, namespaces=NSMAP)
        if not lang_trans is None:
            return lang_trans
    default_trans = tree.xpath('//xf:translation[@default=\'true()\']/xf:text', namespaces=NSMAP)
    if not default_trans is None:
        return default_trans
    return tree.xpath('//xf:translation[1]/xf:text', namespaces=NSMAP)
        
labels = { t.attrib['id']: label_value(t) for t in find_labels(args.lang) }

trans_re = re.compile('jr[:]itext[(][\'"](.*?)[\'"][)]')

def label_text(l):
    if 'ref' in l.attrib:
        return trans_re.sub(
            lambda m: labels[m.group(1)] if m.group(1) in labels else '{%s}' % m.group(1),
            l.attrib['ref'])
    return l.text

for select in tree.xpath('//xf:select|//xf:select1', namespaces=NSMAP):
    question_label = select.find('xf:label', namespaces=NSMAP)
    print('\n(%s) %s\n' % (select.attrib['ref'], label_text(question_label)))
    items = select.findall('xf:item', namespaces=NSMAP)
    for item in items:
        item_label = label_text(item.find('xf:label', namespaces=NSMAP))
        value = item.find('xf:value', namespaces=NSMAP).text
        print("    %s: %s" % (value, item_label))
    itemset = select.find('xf:itemset', namespaces=NSMAP)
    if not itemset is None:
        items_ref = itemset.attrib['nodeset']
        value_ref = itemset.xpath('xf:value[1]/@ref', namespaces=NSMAP)[0]
        label_ref = itemset.xpath('xf:label[1]/@ref', namespaces=NSMAP)[0]
        print("    [itemset: %s]\n    %s: %s" % (itemset.attrib['nodeset'], value_ref, label_ref))

