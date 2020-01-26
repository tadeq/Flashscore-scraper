from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException
import time

browser = webdriver.Firefox(executable_path='geckodriver-v0.26.0-linux64/geckodriver')
main_url = 'https://www.flashscore.com'


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


def get_season_matches_as_html(link):
    browser.get(link)
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


def scrape_table(season_table):
    pass


def scrape_data(season, season_matches):
    teams = []
    matches = []


if __name__ == '__main__':
    browser.get(main_url)
    more_countries_element = browser.find_element_by_class_name('show-more')
    more_countries_button = more_countries_element.find_element_by_link_text('More')
    execute_script_click(more_countries_button)

    click_league('England', 'Premier League')

    archive_button = browser.find_element_by_link_text('Archive')
    archive_button.click()

    season_names = browser.find_elements_by_class_name('leagueTable__season')[2:]
    season_names = [season.find_element_by_tag_name('a') for season in season_names]
    links = [season.get_attribute('href') for season in season_names][::-1]
    season_matches = get_season_matches_as_html(links[0])
    for match in season_matches:
        print(match.prettify())

    browser.quit()
