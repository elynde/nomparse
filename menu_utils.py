#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2
import json
import time
import datetime
import re
import sets

def get_raw_post_data_for_page(page):
  response = urllib2.urlopen('https://graph.facebook.com/%s/posts?access_token=229283283924368|' % page + open('appsecret_DO_NOT_CHECK_IN').read())
  return json.load(response)['data']

def is_menu(post):
  if not 'message' in post:
    return False
  text = post['message'].lower()
  easy = 'dinner' in text or 'lunch' in text or 'breakfast' in text or 'happy hour' in text
  if easy:
    return True

  # This bit us, hard. https://www.facebook.com/FBNYCCafe/posts/716949518339941
  return get_sections(post['message']) > 3

def is_cafe_ltd(post):
  m = re.search('L[^a-z]?T[^a-z]?D', post['message'], re.IGNORECASE);
  if m != None:
    return True

  return re.search(u"livin[g'’]? the dream", post['message'], re.IGNORECASE) != None

def get_most_recent_menu_raw(cafe):
  posts = None
  if cafe == 'nyc':
    f = is_menu
    posts = get_raw_post_data_for_page('fbnyccafe')
  elif cafe == 'epic':
    posts = get_raw_post_data_for_page('FacebookCulinaryTeam')
    f = lambda p: is_menu(p) and 'epic' in p['message'].lower()
  elif cafe == 'ltd':
    posts = get_raw_post_data_for_page('FacebookCulinaryTeam')
    f = lambda p: is_menu(p) and is_cafe_ltd(p)
  elif cafe == 'seattle':
    f = is_menu
    posts = get_raw_post_data_for_page('fbseattlecafe')

  for p in posts:
    if f(p):
      return p
  return None

def get_most_recent_menu(cafe):
  raw = get_most_recent_menu_raw(cafe)
  if raw == None:
    return {}

  lines = raw['message'].split('\n')
  sections = []
  curr_section = None
  header_lines = []
  for i, line in enumerate(lines):
    prev_line = None
    next_line = None
    if line.strip() == '':
      continue
    if i != 0:
      prev_line = lines[i-1]
    if i != len(lines) -1:
      next_line = lines[i+1]
    if section_header_probability(line, prev_line, next_line) > .5:
      if curr_section:
        sections.append(curr_section)
      curr_section = { 'name': line.replace('~', '').strip(), 'items': [] }
    else:
      if curr_section:
        curr_section['items'].append(line.replace('*', '').strip())
      else:
        header_lines.append(line.replace('~', '').replace('*', '').strip())

  return { 'header': "\n".join(header_lines), 'sections' : sections }

def section_header_probability(line, prev_line, next_line):
  common_sections_regexes = sets.Set([u'entr[ée]es?', 'soup?s', u'veg[^ ]* entr[ée]es?', 'starch(es)?', 'dessert(s)?', 'smoothie?s', 'pastr(y|ie)', 'specials', 'healthy options?', 'asian line', 'salads?', 'sides', 'treat yo', 'juice badger'])

  if line.strip() == '':
    return 0
 
  # This should factor into the below algo but these are always actual
  # items since they signify healthy/unhealthy
  starts_with_stars = re.search('^[ ]*\*', line) != None
  if starts_with_stars:
    return 0

  if line.replace('-', '').replace('~', '').strip().lower() == 'enjoy':
    return 0

  has_common_name = False 
  for regex in common_sections_regexes:
    if re.search(regex, line, re.IGNORECASE) != None:
      has_common_name = True
      break

  prev_line_blank = prev_line != None and prev_line.strip() == ''
  next_line_not_blank = next_line != None and next_line.strip() != ''
  ends_in_colon = re.search(':$', line) != None
  starts_with_tildes = re.search('^[ ]*~', line) != None
  short_line = len(line) < 15
  all_caps = line.upper() == line

  features = [(.75, has_common_name), (.8, prev_line_blank), (.25, next_line_not_blank), (.15, ends_in_colon), (.4, starts_with_tildes), (.25, short_line), (.1, all_caps)]

  feature_sum = 0
  total = 0
  for i, (p, feature) in enumerate(features):
    total += p
    if feature:
      feature_sum += p

  return feature_sum/total

def get_sections(post):
  lines = post.split('\n')
  sections = []
  for i, line in enumerate(lines):
    prev_line = None
    next_line = None
    if i != 0:
      prev_line = lines[i-1]
    if i != len(lines) -1:
      next_line = lines[i+1]
    if section_header_probability(line, prev_line, next_line) > .5:
      sections.append(line)
  return sections
