from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re
from model import Team, Match, TableEntry, Table, Season, TeamStats, League
from db_connection import DatabaseConnection

browser = webdriver.Firefox(executable_path='geckodriver-v0.26.0-linux64/geckodriver')
main_url = 'https://www.flashscore.com'
db = DatabaseConnection('test.db')


def execute_script_click(button):
    browser.execute_script('arguments[0].click();', button)


def click_league(country, league):
    left_panel = browser.find_element_by_id('lc')
    countries_menus = left_panel.find_elements_by_class_name('mbox0px')
    countries_lists = [menu.find_element_by_class_name('menu') for menu in countries_menus]
    countries_lists = [countries_list for countries_list in countries_lists]
    found_countries = [element.find_elements_by_link_text(country) for element in countries_lists]
    found_countries = [found_country for found_country in found_countries if len(found_country) > 0]
    if found_countries and found_countries[0]:
        found_countries = found_countries[0][0]
    execute_script_click(found_countries)
    league = left_panel.find_element_by_link_text(league)
    league.click()


def get_season_matches_as_html(league_link):
    browser.get(league_link)
    results_tab = browser.find_element_by_link_text('Results')
    results_tab.click()
    more_button = browser.find_element_by_class_name('event__more')
    more_matches = more_button is not None
    while more_matches:
        try:
            browser.execute_script('arguments[0].click();', more_button)
            time.sleep(3)
        except StaleElementReferenceException as exc:
            more_matches = False
    source = browser.find_element_by_class_name('event').get_attribute('innerHTML')
    soup = BeautifulSoup(source, 'lxml')
    match_divs = soup.find_all('div', class_='event__match')
    return match_divs


def get_team_by_name(teams, name):
    for team in teams:
        if team.name == name:
            return team
    return None


def get_table_entries_from_table_row(table_row_soup):
    place = table_row_soup.find('div', class_='table__cell--rank')
    print(place.text.strip())
    table_row_soup.find('span', class_='team_name_span')


def get_team_stats_from_table_row(table_row):
    pass


def scrape_table(league_link, league, season):
    browser.get(league_link)
    standings_tab = browser.find_element_by_link_text('Standings')
    standings_tab.click()
    WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'table__body')))
    source = browser.find_element_by_class_name('table__body').get_attribute('innerHTML')
    soup = BeautifulSoup(source, 'lxml')
    table_rows = soup.find_all('div', class_='table__row')
    table_entries = [get_table_entries_from_table_row(row) for row in table_rows]
    teams_stats = [get_team_stats_from_table_row(row) for row in table_rows]


def scrape_data(season, season_matches):
    teams = []
    matches = []


def get_years_from_season_name(season_name):
    return re.search('[0-9][0-9][0-9][0-9]/[0-9][0-9][0-9][0-9]', season_name).group()


if __name__ == '__main__':
    league_name = 'Premier League'

    browser.get(main_url)
    more_countries_element = browser.find_element_by_class_name('show-more')
    more_countries_button = more_countries_element.find_element_by_link_text('More')
    execute_script_click(more_countries_button)

    click_league('England', league_name)

    archive_button = browser.find_element_by_link_text('Archive')
    archive_button.click()

    season_names = browser.find_elements_by_class_name('leagueTable__season')[2:]
    season_names = [season.find_element_by_tag_name('a') for season in season_names]
    league = League(name=league_name)
    seasons = [Season(name=get_years_from_season_name(season_name.text), league=league) for season_name in season_names]

    links = [season.get_attribute('href') for season in season_names][::-1]

    scrape_table(links[0], league, seasons[0])

    # season_matches = get_season_matches_as_html(links[0])
    # for match in season_matches:
    #     print(match.prettify())

    browser.quit()
