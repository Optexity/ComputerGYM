from computergym import BrowserEnvTypes, EnvTypes, OpenEndedWebsite, make_env

# with open(
#     "/Users/sankalp/repository/github/Reinforce-Align-AI/playwright/playwright_recorder_output/22x32m0ulva6dhtfluuz43.html",
#     "r",
# ) as f:
#     saved_html = f.read()
# url = "https://www.amazon.com/s?i=luxury&bbn=20722894011&rh=n%3A20722894011%2Cp_123%3A543860&dc&fs=true&ds=v1%3AFObbiyEDFghL4O9cgBrmU%2F8dlGvI6cnRkQ3Zn2K7lMM&_encoding=UTF8&_encoding=UTF8&content-id=amzn1.sym.f939aff9-0ba7-4f55-a9da-072f3c49e556&pd_rd_r=4f80e985-a745-4599-a6e3-6a6a02646924&pd_rd_w=SHuhA&pd_rd_wg=Gk6kl&pf_rd_p=f939aff9-0ba7-4f55-a9da-072f3c49e556&pf_rd_r=DYPV6RM566HRPHPK74N4&qid=1739989843&rnid=85457740011&ref=pd_hp_d_atf_unk"
# env: OpenEndedWebsite = make_env(
#     None,
#     EnvTypes.browser,
#     BrowserEnvTypes.openended,
#     cache_dir=None,
#     goal_message=None,
#     headless=True,
# )
# env.reset()

# env.page.route("**/*", lambda route: route.abort())
# env.page.set_content(saved_html, wait_until="domcontentloaded")
# env.get_obs()
# element = env.page.locator('[data-test-id="deals"]')
# print(element.text_content())
# print(element.get_attribute("bid"))
# print("\n\n\n-------\n\n\n")
# env.close()


env: OpenEndedWebsite = make_env(
    "https://hubspot.com",
    EnvTypes.browser,
    BrowserEnvTypes.openended,
    cache_dir=None,
    goal_message=None,
    headless=False,
)
obs, info = env.reset()
with open("temp.html", "w") as f:
    f.write(env.page.content())
exit()
# env.get_obs()
breakpoint()
element = env.page.locator('[data-test-id="deals"]')
print(element.text_content())
print(element.get_attribute("bid"))
print("\n\n\n-------\n\n\n")
env.close()
