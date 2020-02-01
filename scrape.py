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


def get_table_entries_from_table_div(table_rows_soup, league, table):
    teams_with_places = {}
    for row in table_rows_soup:
        place = row.find('div', class_='table__cell--rank').text.strip()
        team_name = row.find('span', class_='team_name_span').a.text
        teams_with_places[team_name] = place
    teams = db.get_teams_by_league_and_names(league, list(teams_with_places))
    return [TableEntry(table=table, team=team, place=teams_with_places[team.name]) for team in teams]


def find_team_by_name(teams, name):
    for team in teams:
        if team.name == name:
            return team
    return None


def get_team_stats_from_table_div(table_rows_soup, season, teams):
    teams_stats = []
    for row in table_rows_soup:
        team_name = row.find('span', class_='team_name_span')
        team_name = team_name.a.text
        team = find_team_by_name(teams, team_name)
        matches_played = row.find('div', class_='table__cell--matches_played').text
        wins = row.find('div', class_='table__cell--wins_regular').text
        draws = row.find('div', class_='table__cell--draws').text
        losses = row.find('div', class_='table__cell--losses_regular').text
        goals = row.find('div', class_='table__cell--goals').text.split(':')
        goals_scored = goals[0]
        goals_conceded = goals[1]
        points = row.find('div', class_='table__cell--points').text
        stats = TeamStats(team=team, season=season, matches_played=matches_played, wins=wins, draws=draws,
                          losses=losses, goals_scored=goals_scored, goals_conceded=goals_conceded, points=points)
        teams_stats.append(stats)
    return teams_stats


def scrape_table(league_link, league, season):
    browser.get(league_link)
    standings_tab = browser.find_element_by_link_text('Standings')
    standings_tab.click()
    inner_standings = browser.find_element_by_id('tabitem-table')
    inner_standings.click()
    WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'table__body')))
    source = browser.find_element_by_class_name('table__body').get_attribute('innerHTML')
    soup = BeautifulSoup(source, 'lxml')
    table_rows = soup.find_all('div', class_='table__row')
    table = Table(season=season)
    table_entries = get_table_entries_from_table_div(table_rows, league, table)
    db.save_table_entries(table_entries)
    teams = [entry.team for entry in table_entries]
    teams_stats = get_team_stats_from_table_div(table_rows, season, teams)
    db.save_team_stats(teams_stats)


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


def get_match_year(season, date):
    date_month = int(date.split('.')[1])
    season_years = season.name.split('/')
    return date + season_years[0] if date_month < 7 else date + season_years[1]


# has to be done after scrape_table where teams are loaded to database
def scrape_results(league_link, season):
    teams = db.get_teams_by_season(season)
    matches_soup = get_season_matches_as_html(league_link)
    matches = []
    for match_div in matches_soup:
        date_time = match_div.find('div', class_='event__time').text
        date = get_match_year(season, date_time.split(' ')[0])
        home_team_name = match_div.find('div', class_='event__participant--home').text
        away_team_name = match_div.find('div', class_='event__participant--away').text
        home_team = find_team_by_name(teams, home_team_name)
        away_team = find_team_by_name(teams, away_team_name)
        score = match_div.find('div', class_='event__scores').text.replace(' ', '').split('-')
        home_team_score = score[0]
        away_team_score = score[1]
        match = Match(season=season, date=date, home_team=home_team, away_team=away_team,
                      home_team_score=home_team_score, away_team_score=away_team_score)
        matches.append(match)
    db.save_matches(matches)


def get_years_from_season_name(season_name):
    return re.search('[0-9][0-9][0-9][0-9]/[0-9][0-9][0-9][0-9]', season_name).group()


if __name__ == '__main__':
    league_name = 'Premier League'
    db.delete_league_by_name(league_name)

    browser.get(main_url)
    more_countries_element = browser.find_element_by_class_name('show-more')
    more_countries_button = more_countries_element.find_element_by_link_text('More')
    execute_script_click(more_countries_button)

    click_league('England', league_name)

    archive_button = browser.find_element_by_link_text('Archive')
    archive_button.click()

    season_names = browser.find_elements_by_class_name('leagueTable__season')[2:]
    season_names = [season.find_element_by_tag_name('a') for season in season_names][::-1]

    league = League(name=league_name)
    db.save_league(league)

    seasons = [Season(name=get_years_from_season_name(season_name.text), league=league) for season_name in season_names]

    links = [season.get_attribute('href') for season in season_names]

    scrape_table(links[0], league, seasons[0])
    scrape_results(links[0], seasons[0])

    browser.quit()
