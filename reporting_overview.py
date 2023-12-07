from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re
import moment
from selenium.common.exceptions import NoSuchElementException

options = webdriver.ChromeOptions()
options.add_experimental_option("detach", True)
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 10)

driver.get("https://worklenz.com/auth")
driver.maximize_window()

team_indexes = []
total_projects_count = []
teams_members = []

teams_details = []  # type team
Active_projects = []
OverDue_projects = []


def main():
    login()
    go_to_reporting()


def login():
    wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@placeholder='Email']"))).send_keys(
        "coyonic318@hupoi.com")
    wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@placeholder='Password']"))).send_keys(
        "Test@12345")
    wait.until(EC.visibility_of_element_located((By.XPATH, "//span[normalize-space()='Log in']"))).click()
    time.sleep(5)


def go_to_reporting():
    wait.until(
        EC.visibility_of_element_located((By.XPATH, "//strong[normalize-space()='Reporting']"))).click()
    time.sleep(10)


def go_to_settings_team_members():
    wl_header = driver.find_element(By.TAG_NAME, "worklenz-header")
    left_header = wl_header.find_elements(By.TAG_NAME, "ul")[1]
    profile_icon = left_header.find_elements(By.TAG_NAME, "li")[-1]
    profile_icon.click()
    time.sleep(1)
    drop_down_menu = driver.find_element(By.CSS_SELECTOR,
                                         "ul[class='ant-menu ant-menu-root ant-menu-light ant-menu-vertical']")
    drop_down_menu.find_elements(By.TAG_NAME, "li")[1].click()
    time.sleep(5)
    settings_side_bar = driver.find_element(By.TAG_NAME, "nz-sider")
    team_members_tab = settings_side_bar.find_elements(By.TAG_NAME, "li")[8]
    team_members_tab.click()
    time.sleep(2)
    pagination = driver.find_element(By.TAG_NAME, "nz-pagination")
    page_drop_down = pagination.find_elements(By.TAG_NAME, "li")[-1]
    page_drop_down.click()
    time.sleep(2)
    maxi_pages = driver.find_elements(By.TAG_NAME, "nz-option-item")[-1]
    maxi_pages.click()
    time.sleep(3)


def get_team_members():
    table = driver.find_element(By.TAG_NAME, "table")
    tbody = table.find_element(By.TAG_NAME, "tbody")
    rows = tbody.find_elements(By.TAG_NAME, "tr")
    for row in rows:
        cell = row.find_elements(By.TAG_NAME, "td")[2]
        teams_member = cell.text.strip()
        if teams_member not in teams_members:
            teams_members.append(teams_member)


def get_project_end_date():
    end_date = driver.find_element(By.XPATH,
                                   "//div[2]/nz-form-item/nz-form-control/div/div/nz-date-picker/div/input")
    end_date_value = end_date.get_attribute("value")
    if end_date_value == "":
        print("not end date")
    else:
        print(end_date_value)

    drawer_close = driver.find_element(By.XPATH,
                                       "//div[@class='ant-drawer ant-drawer-right ng-star-inserted ant-drawer-open']//span[@class='anticon anticon-close ng-star-inserted']//*[name()='svg']")
    drawer_close.click()
    time.sleep(3)
    return end_date_value


def open_team_selection():
    header = driver.find_element(By.TAG_NAME, "worklenz-header")
    header_div = header.find_elements(By.TAG_NAME, "div")[1]
    header_ul = header_div.find_elements(By.TAG_NAME, "ul")[1]
    team_selection = header_ul.find_elements(By.TAG_NAME, "li")[0]
    team_selection.click()
    time.sleep(5)


def get_owner_you_team():
    ul = driver.find_element(By.CLASS_NAME, "p-0")
    teams = ul.find_elements(By.TAG_NAME, "li")
    for index, team in enumerate(teams):
        owner = team.find_element(By.TAG_NAME, "small")
        Owner_by = owner.text.strip()
        if Owner_by == "Owned by You":

            team_indexes.append(index)


def pagination_count_change():
    pagination = driver.find_element(By.TAG_NAME, "nz-pagination")
    page_drop_down = pagination.find_elements(By.TAG_NAME, "li")[-1]
    page_drop_down.click()
    time.sleep(2)
    page_count = driver.find_elements(By.TAG_NAME, "nz-option-item")[2]
    time.sleep(1)
    page_count.click()
    time.sleep(2)


def get_own_you_teams_project_count():
    i = 0
    while i < len(team_indexes):
        team_ = {
            "id": "",
            "name": "",
            "projects": []
        }
        ul = driver.find_element(By.CLASS_NAME, "p-0")
        teams = ul.find_elements(By.TAG_NAME, "li")
        teams[team_indexes[i]].click()
        time.sleep(2)
        go_to_settings_team_members()
        get_team_members()
        wait.until(EC.visibility_of_element_located((By.XPATH, "//strong[normalize-space()='Projects']"))).click()
        time.sleep(6)
        try:
            pagination_count_change()

        except NoSuchElementException:
            print("Projects not available")

        team_["name"] = "test"
        team_["projects"] = get_project_details()
        teams_details.append(team_)
        page_header_title = driver.find_element(By.TAG_NAME, "nz-page-header-title")
        projects_title = page_header_title.text
        projects_count = re.search(r'\d+', projects_title).group()
        total_projects_count.append(projects_count)
        open_team_selection()
        time.sleep(1)
        i = i + 1


def get_project_details():
    projects = []
    t_body = driver.find_element(By.TAG_NAME, "tbody")
    td_ = t_body.find_element(By.TAG_NAME, "td")
    td_class_name = td_.get_attribute("class")
    if "nz-disable-td" in td_class_name:  # projects available or not
        return projects
    else:
        rows = t_body.find_elements(By.TAG_NAME, "tr")
        for row in rows:
            icons = row.find_element(By.TAG_NAME, "nz-space")
            settings = icons.find_elements(By.TAG_NAME, "div")[0]
            settings.click()
            time.sleep(2)
            project = {
                "name": "",
                "start_date": "",
                "end_date": "",
                "is_overdue": False
            }

            project_name = driver.find_element(By.XPATH, "//div/input")
            project_end_date = driver.find_element(By.XPATH,
                                                   "//div[2]/nz-form-item/nz-form-control/div/div/nz-date-picker/div/input")
            project_start_date = driver.find_element(By.XPATH,
                                                     "//div[1]/nz-form-item/nz-form-control/div/div/nz-date-picker/div/input")
            project_name_text = project_name.get_attribute("value")
            project_end_date_text = project_end_date.get_attribute("value")
            project_start_date_text = project_start_date.get_attribute("value")

            project["name"] = project_name_text
            project["start_date"] = project_start_date_text
            project["end_date"] = project_end_date_text

            if project_end_date_text.strip() == "":
                project["is_overdue"] = False
            else:
                project["is_overdue"] = check_date_is_before(project_end_date_text.strip())

            projects.append(project)
            drawer_close = driver.find_element(By.XPATH,
                                               "//div[@class='ant-drawer ant-drawer-right ng-star-inserted ant-drawer-open']//span[@class='anticon anticon-close ng-star-inserted']//*[name()='svg']")
            drawer_close.click()

        pagination = driver.find_element(By.TAG_NAME, "nz-pagination")
        next_btn = pagination.find_element(By.CLASS_NAME, "ant-pagination-next")
        button = next_btn.find_element(By.TAG_NAME, "button")
        if button.is_enabled():
            next_btn.click()
            time.sleep(5)
            projects += get_project_details()  # combine value to array
            time.sleep(3)

        return projects

    # write code if projects not
    # write code for pagination


def check_date_is_before(end_date):
    f_end_date = moment.date(end_date)
    today = moment.now()
    f_end_date_without_time = f_end_date.strftime("%Y-%m-%d")
    today_date_without_time = today.strftime("%Y-%m-%d")
    if f_end_date_without_time >= today_date_without_time:
        return False
    else:
        return True


def get_reporting_overview_first_card_details():
    overview_cards = driver.find_element(By.TAG_NAME, "worklenz-rpt-overview-cards")
    first_card = overview_cards.find_elements(By.TAG_NAME, "nz-card")[0]
    teams_details = first_card.find_element(By.CLASS_NAME, "ant-card-meta-title")
    teams_title = teams_details.text.strip()
    teams_count_reporting = re.search(r'\d+', teams_title).group()  # get only number

    projects_card_description = first_card.find_element(By.CLASS_NAME, "ant-card-meta-description")
    projects = projects_card_description.find_elements(By.TAG_NAME, "p")[0]
    project_count_reporting = re.search(r'\d+', projects.text.strip()).group()

    members = projects_card_description.find_elements(By.TAG_NAME, "p")[1]
    members_count_reporting = re.search(r'\d+', members.text.strip()).group()

    return teams_count_reporting, project_count_reporting, members_count_reporting


def get_active_overdue_projects_count():
    for team_details in teams_details:
        for project in team_details["projects"]:
            if project['is_overdue']:
                OverDue_projects.append(project)

            else:
                Active_projects.append(project)

            time.sleep(1)


def get_reporting_active_overdue_projects_count():
    overview_cards = driver.find_element(By.TAG_NAME, "worklenz-rpt-overview-cards")
    second_card = overview_cards.find_elements(By.TAG_NAME, "nz-card")[1]
    projects_description = second_card.find_element(By.CLASS_NAME, "ant-card-meta-description")
    active_projects = projects_description.find_elements(By.TAG_NAME, "p")[0]
    active_projects_count = re.search(r'\d+', active_projects.text.strip()).group()
    overdue_projects = projects_description.find_elements(By.TAG_NAME, "p")[1]
    overdue_projects_count = re.search(r'\d+', overdue_projects.text.strip()).group()
    return active_projects_count, overdue_projects_count


def get_reporting_overview_second_card_details():
    overview_cards = driver.find_element(By.TAG_NAME, "worklenz-rpt-overview-cards")
    second_card = overview_cards.find_elements(By.TAG_NAME, "nz-card")[1]
    projects_details = second_card.find_element(By.CLASS_NAME, "ant-card-meta-title")
    projects_title = projects_details.text.strip()
    s_card_project_count_reporting = re.search(r'\d+', projects_title).group()
    return s_card_project_count_reporting


def check_overview_first_card(r_team_count, r_project_count, r_member_count):
    int_team_count = int(r_team_count)
    print("Reporting Overview team count = ", int_team_count)
    print("Your actual own teams = ", len(team_indexes))
    if int_team_count == len(team_indexes):
        print("Team count is correct")

    else:
        print("Team count is wrong")

    sum_of_projects_count = sum(int(num) for num in total_projects_count)
    int_project_count = int(r_project_count)
    print("Reporting Overview projects count = ", int_project_count)
    print("Your actual projects count = ", sum_of_projects_count)
    if int_project_count == sum_of_projects_count:
        print("Project count is correct")

    else:
        print("Project count is wrong")

    int_member_count = int(r_member_count)
    print("Reporting Overview members count = ", int_member_count)
    print("Your actual team members count = ", len(teams_members))
    if int_member_count == len(teams_members):

        print("Teams members count is correct")

    else:
        print("Team members count is wrong")


def check_active_overdue_projects_count(active_projects_no, overdue_projects_no):
    int_active_projects_no = int(active_projects_no)
    int_overdue_projects_no = int(overdue_projects_no)

    print("Reporting Overview Active projects count = ", int_active_projects_no)
    print("Your actual Active projects count = ", len(Active_projects))
    if len(Active_projects) == int_active_projects_no:
        print("Active projects count is correct")

    else:
        print("Active projects count is wrong")

    print("Reporting Overview Overdue projects count = ", int_overdue_projects_no)
    print("Your actual Overview projects count = ", len(OverDue_projects))
    if len(OverDue_projects) == int_overdue_projects_no:
        print("Overdue projects count is correct")

    else:
        print("Overdue projects count is wrong")


main()
open_team_selection()
get_owner_you_team()
get_own_you_teams_project_count()
go_to_reporting()

reporting_team_count, reporting_project_count, members_count_reporting = get_reporting_overview_first_card_details()
check_overview_first_card(reporting_team_count, reporting_project_count, members_count_reporting)
get_active_overdue_projects_count()

active_projects_count, overdue_projects_count = get_reporting_active_overdue_projects_count()
check_active_overdue_projects_count(active_projects_count, overdue_projects_count)
