import scrapy
from ..items import Therapist


class PsychologyTodaySpider(scrapy.Spider):
    name = "psychology_today"
    allowed_domains = ["psychologytoday.com"]
    start_urls = ["https://www.psychologytoday.com/us/therapists/indiana", "https://www.psychologytoday.com/us/therapists/minnesota"]

    def parse(self, response):
        for result in response.css("div.results-row"):
            therapist = Therapist()
            therapist["name"] = result.css("a.profile-title::text").get()
            therapist["credentials"] = result.css("div.profile-subtitle-credentials::text").get()
            therapist["phone_number"] = result.css("span.results-row-phone::text").get()
            therapist["psychology_today_profile_link"] = result.css("a.results-row-cta-view::attr(href)").get()
            if therapist["psychology_today_profile_link"] is not None:
                yield scrapy.Request(therapist["psychology_today_profile_link"], callback=self.parse_psychology_today_profile, cb_kwargs={'therapist': therapist})

        next_page = response.css("div.pagination-controls-end a.page-btn::attr(href)").get()
        if next_page is not None:
            yield scrapy.Request(next_page, callback=self.parse)

    def parse_psychology_today_profile(self, response, therapist):
        therapist["address"] = " ".join([s for s in list(dict.fromkeys(response.css("p.address-line::text").getall()).keys()) if s.strip()])
        therapist["session_fee"] = response.css("span.root::text").get()
        therapist["personal_website"] = response.css("button.btn a.link::attr(href)").get()
        yield therapist
