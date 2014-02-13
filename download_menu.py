#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2
import json
import time
import datetime
import re

#response = urllib2.urlopen('https://graph.facebook.com/fbnyccafe/posts?access_token=CAADQiCyw9ZAABAOAPJgmesPnb90SBPDA7D2I4EpTbYkda4XNaZAfTneCtT6W2yUCJeqeJZCy6wGe5F41bJFAipQYalBAmgwgsStpxHUb86WAema6LZAxh4AzHrrbivQUsPF0SNkllN39r3Qd6ZCE9PCXK5wiAEWUj79vqE10mWcQpFiDjmEGtnIITcDfuuCetnVc345bXHQZDZD')
response = open('cached.txt')
posts = json.load(response)['data']

def get_meal(post):
  if 'lunch' in post['message'].lower():
    return 'lunch'
  if 'dinner' in post['message'].lower():
    return 'dinner'
  if 'happy hour' in post['message'].lower():
    return 'happy hour'

  # these are gmt which is five hours ahead
  post_time = time.strptime(p['created_time'], '%Y-%m-%dT%H:%M:%S+0000')
  post_hour = post_time.tm_hour - 5

  if post_hour > 13:
    return 'dinner'

  return 'lunch'

def get_theme(line):
  m = re.search('~([^~\n]*)~', line)
  if m == None:
    m = re.search('-([^-\n]*)-', line)
    if m == None:
      return None
    theme = m.group(1)
    if theme.lower() == 'soup':
      return None
    return theme
  
  theme = m.group(1)
  if theme.lower() == 'soup':
    return None
  return theme

def filter_dumb_theme(theme):
  return theme.lower() == 'soup'

def is_greeting(line):
  m = re.search('good (morning|afternoon|evening)|(for (dinner|lunch|happy hour) (today|tonight):)', line, re.IGNORECASE)
  return m != None or ('tonight' in line.lower() and 'dinner' in line.lower())

def is_warning(line):
  return 'due to ' in line.lower() 

menus = []
for p in posts:
  if 'message' in p:
    message = p['message']
    meal = get_meal(p)
    curr_menu = { 'meal': meal }
    menus.append(curr_menu)
    curr_menu['sections'] = []
    for i, line in enumerate(message.split('\n')):
      sections_started = len(curr_menu['sections']) > 0
      if (not sections_started):
        if (is_warning(line)):
          curr_menu['warning'] = line
          continue
        if (is_greeting(line)):
          continue;
      if ('theme' not in curr_menu):
        theme = get_theme(line)
        if theme != None:
          curr_menu['theme'] = theme
          continue
      m = re.search('^[\s]*~([^\n:]*):?', line, re.IGNORECASE)
      if m != None:
        curr_menu['sections'].append({ 'name' : m.group(1)})
      else:
        m = re.search('^[\s]*-([^\n:]*):?', line, re.IGNORECASE)
        if m != None:
          curr_menu['sections'].append({ 'name' : m.group(1)})
        if line.strip() == '':
          continue
        if len(curr_menu['sections']) == 0:
          if not 'theme' in curr_menu:
            curr_menu['theme'] = ''
          else:
            curr_menu['theme'] += "\n"
          curr_menu['theme'] += line
          continue
        last = curr_menu['sections'][-1]
        if not 'items' in last:
          last['items'] = []
        last['items'].append(line.strip().replace('*', ''))

print json.dumps(menus[0])
