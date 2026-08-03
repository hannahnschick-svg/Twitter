window.CONSOLE_DATA = {
  "institute": "Chronogene Institute",
  "subtitle": "Board Console",
  "generated_at": "Monday 03 August 2026 · 07:00",
  "sample_banner": "SAMPLE DATA. NOTHING HERE IS A REAL RESULT.",
  "director_note": {
    "avatar": "CI",
    "name": "Your Director",
    "subtitle": "Daily note · sent 07:00 every morning",
    "paragraphs": [
      "Good morning. We confirmed one finding overnight and closed off two questions that turned out to be dead ends. Two things need you today, and one of them is holding up a paper.",
      "The methylation team finished the ageing-clock re-analysis. It held up under both checks, so it is now a confirmed finding. **Methylation** is a chemical tag on DNA that changes with age, so it can be used to estimate how fast someone is ageing. Separately, the longevity gene work did not survive: the effect we were chasing is not there at the sample sizes anyone has published, and we have written down why so nobody here spends another month on it.",
      "**Everything else is running.** Spend is tracking at about two thirds of the monthly ceiling. Nothing is broken."
    ]
  },
  "decisions_meta": "2 decisions",
  "decisions": [
    {
      "status": "NEEDS YOU",
      "tag": "HOLDS A PAPER",
      "waiting": "waiting 1 day",
      "title": "Do we submit the ageing-clock paper, and where?",
      "description": "The paper is finished and has passed all three of our internal checks. It is ready to go out. We do not send anything without you, so it is sitting here.",
      "options": [
        {
          "key": "SEND IT",
          "text": "We prepare the submission package and hand it to you to upload. Roughly a week of back and forth after that."
        },
        {
          "key": "HOLD IT",
          "text": "It sits as it is. Nothing degrades, but the finding is one other groups are also working on."
        },
        {
          "key": "PICK A VENUE",
          "text": "Tell us the journal and we reformat to fit it. Adds about two days."
        }
      ],
      "if_nothing": "the paper stays held and we ask again on Friday.",
      "actions": [
        {
          "label": "Send it",
          "primary": true
        },
        {
          "label": "Hold it"
        },
        {
          "label": "I have a venue in mind"
        }
      ]
    },
    {
      "status": "NEEDS YOU",
      "tag": "COSTS MONEY",
      "waiting": "waiting 4 hours",
      "title": "Should we pay for faster access to one literature database?",
      "description": "Our literature scanning is free but rate-limited, so a full sweep takes about six hours instead of twenty minutes. A paid key costs about 40 dollars a month.",
      "options": [
        {
          "key": "APPROVE",
          "text": "Sweeps finish same morning. Adds 40 dollars a month to a ceiling we are currently under."
        },
        {
          "key": "DECLINE",
          "text": "Nothing breaks. Sweeps stay slow, which delays new questions reaching the lab by about half a day."
        }
      ],
      "if_nothing": "we carry on at the free rate. This is not urgent.",
      "actions": [
        {
          "label": "Approve the 40 a month",
          "primary": true
        },
        {
          "label": "Decline"
        }
      ]
    }
  ],
  "numbers": {
    "title": "The numbers",
    "meta": "Last 30 days",
    "stats": [
      {
        "label": "Confirmed findings",
        "value": "15",
        "suffix": "/ 23 all time",
        "desc": "Claims that survived independent checking.",
        "bar": null
      },
      {
        "label": "Questions ruled out",
        "value": "8",
        "suffix": "",
        "desc": "Dead ends closed and written down. These count as output, not failure.",
        "bar": null
      },
      {
        "label": "Results that reproduced first time",
        "value": "100",
        "suffix": "%",
        "desc": "A second team re-runs every result from scratch. **Target 90 or above.**",
        "bar": 1.0
      },
      {
        "label": "Every claim backed by evidence",
        "value": "100",
        "suffix": "%",
        "desc": "Each claim traces to a specific result. **Anything under 100 is an alarm.**",
        "bar": 1.0
      },
      {
        "label": "Question to answer",
        "value": "18",
        "suffix": "days median",
        "desc": "From asking a question to having a checked answer.",
        "bar": null
      },
      {
        "label": "Cost per confirmed finding",
        "value": "$123",
        "suffix": "",
        "desc": "Total spend divided by findings that survived checking.",
        "bar": null
      }
    ]
  },
  "answers_chart": {
    "title": "Answers produced each month",
    "subtitle": "Confirmed findings plus questions ruled out. Both are answers, so both are counted.",
    "highlight_last": true,
    "bars": [
      {
        "label": "Mar",
        "value": 6
      },
      {
        "label": "Apr",
        "value": 9
      },
      {
        "label": "May",
        "value": 8
      },
      {
        "label": "Jun",
        "value": 14
      },
      {
        "label": "Jul",
        "value": 15
      },
      {
        "label": "Aug\nso far",
        "value": 18
      }
    ]
  },
  "evidence": {
    "title": "How strong the evidence is",
    "subtitle": "All 15 confirmed findings, by how much weight they can carry.",
    "segments": [
      {
        "count": 4,
        "label": "Strongest. Repeated in separate data. Can carry a paper."
      },
      {
        "count": 6,
        "label": "Solid. One well-powered study, not yet repeated."
      },
      {
        "count": 3,
        "label": "Promising. Rests on one data source or one assumption."
      },
      {
        "count": 2,
        "label": "Early. Suggestive only. Never the headline of a paper."
      }
    ]
  },
  "learned": {
    "title": "What we learned",
    "meta": "Newest first",
    "items": [
      {
        "badge": "RULED OUT",
        "strength": null,
        "time": "day 4",
        "title": "A published link between one gene variant and lifespan does not hold up.",
        "desc": "The original claim traces back to a single small study cited many times without re-testing. We re-tested it. It does not replicate.",
        "caveat": null
      },
      {
        "badge": "RULED OUT",
        "strength": null,
        "time": "day 3",
        "title": "The telomere gene we were chasing does not explain the ageing signal.",
        "desc": "Tested properly and it is not there. The study was large enough that a real effect of the claimed size would have shown. Written up so nobody here repeats it.",
        "caveat": null
      },
      {
        "badge": "CONFIRMED",
        "strength": "SOLID",
        "time": "day 2",
        "title": "People whose blood shows faster ageing also carry a stronger family history of long life, in the opposite direction to what was expected.",
        "desc": "Checked by two separate teams. The effect is small but consistent, and it survived adjusting for the obvious explanations including smoking and blood cell counts.",
        "caveat": "Holds for: people of European ancestry, aged 42 to 69, measured in blood."
      },
      {
        "badge": "CONFIRMED",
        "strength": "STRONGEST",
        "time": "day 1",
        "title": "A regulatory region near a known longevity gene is switched on differently in older tissue, and the pattern repeats across three independent datasets.",
        "desc": "Repeated in data from three separate studies that do not share people, which is why this one is rated strongest. It is the central claim of the paper waiting on you.",
        "caveat": "Holds for: blood and liver tissue, ages 40 to 80. Not shown in brain."
      },
      {
        "badge": "CONFIRMED",
        "strength": "STRONGEST",
        "time": "day 0",
        "title": "Archived confirmed finding 5",
        "desc": "Confirmed in an earlier cycle; retained for the running totals.",
        "caveat": null
      },
      {
        "badge": "RULED OUT",
        "strength": null,
        "time": "day 0",
        "title": "Archived confirmed finding 6",
        "desc": "Confirmed in an earlier cycle; retained for the running totals.",
        "caveat": null
      },
      {
        "badge": "CONFIRMED",
        "strength": "SOLID",
        "time": "day 0",
        "title": "Archived confirmed finding 7",
        "desc": "Confirmed in an earlier cycle; retained for the running totals.",
        "caveat": null
      },
      {
        "badge": "CONFIRMED",
        "strength": "PROMISING",
        "time": "day 0",
        "title": "Archived confirmed finding 8",
        "desc": "Confirmed in an earlier cycle; retained for the running totals.",
        "caveat": null
      },
      {
        "badge": "RULED OUT",
        "strength": null,
        "time": "day 0",
        "title": "Archived confirmed finding 9",
        "desc": "Confirmed in an earlier cycle; retained for the running totals.",
        "caveat": null
      },
      {
        "badge": "CONFIRMED",
        "strength": "STRONGEST",
        "time": "day 0",
        "title": "Archived confirmed finding 10",
        "desc": "Confirmed in an earlier cycle; retained for the running totals.",
        "caveat": null
      },
      {
        "badge": "CONFIRMED",
        "strength": "SOLID",
        "time": "day 0",
        "title": "Archived confirmed finding 11",
        "desc": "Confirmed in an earlier cycle; retained for the running totals.",
        "caveat": null
      },
      {
        "badge": "RULED OUT",
        "strength": null,
        "time": "day 0",
        "title": "Archived confirmed finding 12",
        "desc": "Confirmed in an earlier cycle; retained for the running totals.",
        "caveat": null
      },
      {
        "badge": "CONFIRMED",
        "strength": "PROMISING",
        "time": "day 0",
        "title": "Archived confirmed finding 13",
        "desc": "Confirmed in an earlier cycle; retained for the running totals.",
        "caveat": null
      },
      {
        "badge": "CONFIRMED",
        "strength": "EARLY",
        "time": "day 0",
        "title": "Archived confirmed finding 14",
        "desc": "Confirmed in an earlier cycle; retained for the running totals.",
        "caveat": null
      },
      {
        "badge": "RULED OUT",
        "strength": null,
        "time": "day 0",
        "title": "Archived confirmed finding 15",
        "desc": "Confirmed in an earlier cycle; retained for the running totals.",
        "caveat": null
      },
      {
        "badge": "CONFIRMED",
        "strength": "SOLID",
        "time": "day 0",
        "title": "Archived confirmed finding 16",
        "desc": "Confirmed in an earlier cycle; retained for the running totals.",
        "caveat": null
      },
      {
        "badge": "CONFIRMED",
        "strength": "SOLID",
        "time": "day 0",
        "title": "Archived confirmed finding 17",
        "desc": "Confirmed in an earlier cycle; retained for the running totals.",
        "caveat": null
      },
      {
        "badge": "RULED OUT",
        "strength": null,
        "time": "day 0",
        "title": "Archived confirmed finding 18",
        "desc": "Confirmed in an earlier cycle; retained for the running totals.",
        "caveat": null
      },
      {
        "badge": "CONFIRMED",
        "strength": "EARLY",
        "time": "day 0",
        "title": "Archived confirmed finding 19",
        "desc": "Confirmed in an earlier cycle; retained for the running totals.",
        "caveat": null
      },
      {
        "badge": "CONFIRMED",
        "strength": "STRONGEST",
        "time": "day 0",
        "title": "Archived confirmed finding 20",
        "desc": "Confirmed in an earlier cycle; retained for the running totals.",
        "caveat": null
      },
      {
        "badge": "RULED OUT",
        "strength": null,
        "time": "day 0",
        "title": "Archived confirmed finding 21",
        "desc": "Confirmed in an earlier cycle; retained for the running totals.",
        "caveat": null
      },
      {
        "badge": "CONFIRMED",
        "strength": "SOLID",
        "time": "day 0",
        "title": "Archived confirmed finding 22",
        "desc": "Confirmed in an earlier cycle; retained for the running totals.",
        "caveat": null
      },
      {
        "badge": "CONFIRMED",
        "strength": "PROMISING",
        "time": "day 0",
        "title": "Archived confirmed finding 23",
        "desc": "Confirmed in an earlier cycle; retained for the running totals.",
        "caveat": null
      }
    ]
  },
  "papers": {
    "title": "Papers",
    "meta": "3 in progress · 1 waiting on you",
    "items": [
      {
        "status": "WAITING ON YOU",
        "meta": "ready 1 day",
        "title": "Ageing signals in a longevity-linked gene region",
        "stages": [
          {
            "name": "Written",
            "state": "done"
          },
          {
            "name": "Statistics checked",
            "state": "done"
          },
          {
            "name": "Re-run from scratch",
            "state": "done"
          },
          {
            "name": "Integrity checked",
            "state": "done"
          },
          {
            "name": "Your decision",
            "state": "current"
          }
        ],
        "desc": "Built on 6 confirmed findings   ·   4 figures, all with their underlying numbers attached"
      },
      {
        "status": "IN CHECKING",
        "meta": "3 days in review",
        "title": "What blood can and cannot tell you about ageing in other tissues",
        "stages": [
          {
            "name": "Written",
            "state": "done"
          },
          {
            "name": "Statistics checked",
            "state": "done"
          },
          {
            "name": "Being re-run from scratch",
            "state": "current"
          },
          {
            "name": "Integrity check",
            "state": "pending"
          },
          {
            "name": "Your decision",
            "state": "pending"
          }
        ],
        "desc": "One comment back from the statistics check: a caveat that is in the results needs to be in the summary too. Being fixed."
      },
      {
        "status": "BEING WRITTEN",
        "meta": "started 8 days ago",
        "title": "Three widely cited longevity claims that do not replicate",
        "stages": [
          {
            "name": "Being written",
            "state": "current"
          },
          {
            "name": "Statistics check",
            "state": "pending"
          },
          {
            "name": "Re-run",
            "state": "pending"
          },
          {
            "name": "Integrity check",
            "state": "pending"
          },
          {
            "name": "Your decision",
            "state": "pending"
          }
        ],
        "desc": "Built entirely from questions we ruled out. Negative results are harder to publish and more useful than most of what gets published."
      }
    ]
  },
  "costs": {
    "title": "What it costs",
    "meta": "August, 12 days in",
    "cards": [
      {
        "label": "Spent this month",
        "value": "$1,847",
        "desc": "Against a ceiling of **$4,400**. On pace for about $4,100.",
        "bar": 0.42,
        "accent": false
      },
      {
        "label": "Spent yesterday",
        "value": "$168",
        "desc": "Heavier than usual. The paper going through all three checks at once.",
        "bar": null,
        "accent": false
      },
      {
        "label": "Teams at their daily limit",
        "value": "1",
        "suffix": "of 20",
        "desc": "The literature team hit its cap yesterday. Related to the database decision above.",
        "bar": null,
        "accent": true
      }
    ]
  },
  "lab": {
    "title": "The lab right now",
    "meta": "6 working",
    "teams": [
      {
        "name": "Genetics group",
        "desc": "Working on two questions about how gene variants change function",
        "status": "RUNNING",
        "dot": "green"
      },
      {
        "name": "Epigenetics group",
        "desc": "Just delivered the confirmed finding above",
        "status": "RUNNING",
        "dot": "green"
      },
      {
        "name": "Ageing group",
        "desc": "Waiting on the literature team for a background check",
        "status": "HELD UP",
        "dot": "amber"
      },
      {
        "name": "Analysis core",
        "desc": "Three analyses running, one finishing today",
        "status": "RUNNING",
        "dot": "green"
      },
      {
        "name": "Literature scanning",
        "desc": "At its daily limit until midnight",
        "status": "AT LIMIT",
        "dot": "amber"
      },
      {
        "name": "Checkers",
        "desc": "Three independent reviewers. They can stop any result and nobody here can overrule them.",
        "status": "RUNNING",
        "dot": "green"
      }
    ]
  },
  "footer": "**Nothing here leaves the building without you.** The lab cannot submit a paper, post a preprint, publish data, spend money, or contact anyone. It writes files, checks them, and holds them. Every number on this page traces back to a specific result and the exact command that produced it, and any figure that cannot be traced is treated as an alarm rather than a rounding issue."
};
