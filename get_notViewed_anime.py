import requests
import json
import pandas as pd

def getRelatedWorks(token):
  url = 'https://api.annict.com/graphql'
  headers = {'Authorization': f'Bearer {token}'}

  query = """query {
              viewer {
                works(state: WATCHED, orderBy:{field: SEASON, direction:DESC}) {
                  nodes {
                    title,
                    seriesList {
                      nodes {
                        name,
                        works(orderBy:{field:SEASON, direction:ASC}) {
                          edges {
                            summary,
                            node {
                              viewerStatusState,
                              title
                            }
                          }
                        }
                      }
                    }
                  }
                }
              }
            }"""

  return requests.post(url, headers=headers, data={'query': query})


def getNotViewed(token, ignore_list):
  r = getRelatedWorks(token)

  notViewed = []
  set_notViewd = set()

  df = pd.DataFrame(json.loads(r.text)['data']['viewer']['works']['nodes'])
  for i, row in df.iterrows():
    if any(x in row['title'] for x in ignore_list): continue

    df2 = pd.DataFrame(row['seriesList']['nodes'])
    for i2, row2 in df2.iterrows():
      seriesName = row2['name']

      df3 = pd.DataFrame(row2['works']['edges'])
      for i3, row3, in df3.iterrows():
        status = row3['node']['viewerStatusState']
        title = row3['node']['title']
        summary = row3['summary']

        if status == 'NO_STATE':
          if (all(x not in title for x in ignore_list)) and (title not in set_notViewd):
              notViewed.append({f'{seriesName}({summary})': title})
              set_notViewd.add(title)

  return notViewed


if __name__ == '__main__':
  from dotenv import load_dotenv
  import os

  # .envからトークンを入手
  load_dotenv(verbose=True)
  dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
  load_dotenv(dotenv_path)
  token = os.getenv('ANNICT_TOKEN')

  # 無視する作品
  ignore_list = ['ルパン', 'コナン', 'ドラゴンボール', 'ドラえもん', 'HELLO WORLD']

  notViewed = getNotViewed(token, ignore_list)

  for anime in notViewed:
    for summary, title in anime.items():
      print(f'{summary}: {title}')
