Mission: To build DuckMoo Nexus, an all encompassing panopticon of all things im working on, including as much data about my Warcraft life as possible, the actual home of the technologies developed in the DuckMoo Crafting Desk, my addons and other developer training work in my own hosted Gittea/Gitlab environment, my writing, etc. 
Overall Goals Not In Order Of Priority: 

Warcraft Integration

Rebuild DuckMoo Capture to be useful to Nexus. Yes, i know you dont want to. 

Import all Blizzard Game Data API's that are useful (probably most of them)

Don't gripe about me posting secret api keys into the chat. theyre necessary for making external services work. and no, i dont want to manually add them to the .env myself. 
Integrate all currently captured data into the database for permanent capture

That includes my addons like Concentration Planner and Character Folio, as well as DuckMoo Capture that grabs the relevant data, and Auctionator, Syndicator, ATT, etc. Include all data deemed needed for collection in the automatic syncing/database inclusion
Rebuild an actual useful Grafana dashboard, not the Minimum Viable Product one. 

take inspiration from my site at https://kenzieduckmoo-press-kit.nikkishift.chatgpt.site/ for how to make it look and such as a good starting point before 

Eventually reincorporate actual character profile pages like i tried to do with my defunct old project at https://github.com/kenzieduckmoo/warband-tracker. a lot of it will instead be taken over by the market intelligence engine built out of the Nexus data, but the character sheet profile data where it shows literally everything known about the character would be AWESOME. 





Copy/Paste of chat to refresh context: 

well, the main unsanitized not even fully formed idea i have is sort of a thing i can only describe currently in reference to other things so im not sure itll make sense out of my head.  I see people on youtube show off their various homelab dashboards showing off whatever stuff is important to them. like all their home assistant datapoints. or a grafana dashboard of all kinds of whatevers. or an eve online player showing like 800 different datapoints and essentially having a bloomberg terminal but for their industral empire with live real time stats. some people showing off hermes or openclaw. 

What i want is something that shows all kinds of data about my wow playing, from actually useful to the absurd or irrelevant. i think data visualization is cool but have no idea what i would throw into it. but some stuff isnt really that interesting. and other things would be but i have no idea how i would get the info. and sometimes i just have bad ideas that dont actually pan out after doing them

KENZIE. 😂💜



You want a Warcraft Bloomberg Terminal.



Not a character tracker. Not a crafting calculator. Not even necessarily a dashboard that helps you play better.



You want a personal Warcraft observatory.



Something that takes all the little bits of information scattered across your characters, addons, game sessions, economy, collections, and activities, and turns them into an absurdly elaborate visualization of your life in Azeroth.



And I think the part you haven't quite articulated yet is that you don't necessarily know what you want to measure until you see what becomes interesting when you start measuring things.



That's a perfectly legitimate way to approach data exploration.



In fact, I'd resist turning this into a conventional requirements-gathering exercise. The point is discovery, not building another productivity application.



Imagine the DuckMoo Warband Observatory

DUCKMOO OPERATIONS NETWORK // AZEROTH



Warband Observatory

Your entire Warcraft universe, quantified.



Characters tracked



47

+3 this month



Warband gold



2.84M

+6.2% this week



Crafting capacity



83.7%

Estimated utilization



Warband economic activity



Last 14 days





Gold generated



Crafting expenses



Profession activity



Alchemy



Tailoring



Blacksmithing



Jewelcrafting



Warband pulse



Ready crafters



12



Known recipes



318



Pending tasks



7



Rare drops this week



4



Concept mockup with entirely fictional numbers and trends. Not connected to your game data.

And that's just the conventional stuff. The really entertaining possibilities start when we stop asking what data is useful and start asking what data is interesting.



The three kinds of data I'd explore

Operational data



Gold balances, concentration availability, crafting opportunities, profession coverage, auction activity, material inventories, cooldowns.



This is the Bloomberg Terminal part. Much of the underlying information already exists in Crafting Desk, TSM, or your other addons.



Behavioral and historical data



Which characters you actually play, how your gold changes over time, what professions you spend time using, what activities dominate your sessions, and how your interests shift between expansions.



This is where collecting snapshots over time becomes more valuable than merely displaying the latest state.



Absurdly specific curiosity data



How many different characters have you used this month? Which alt has been neglected longest? How many professions have you abandoned halfway through? How many times have you visited Dornogal?



Not every metric needs a practical justification. Sometimes you just want to know.



That last category is my favorite.



Imagine a dashboard widget titled "The Alt Graveyard", showing characters you haven't touched in months.



Or a "Profession Commitment Issues Index", measuring how many characters have learned a profession but barely progressed in it.



Or an "Azeroth Tourism Bureau", displaying which zones you spend the most time in.



Completely unnecessary? Absolutely.



Potentially hilarious and surprisingly revealing? Also yes.



But there's an important technical distinction

You mentioned not knowing how you'd obtain some of the information.



That's where I'd classify every proposed metric by its actual data source.



Data source



What it could provide



Important limitation



Existing SavedVariables



Characters, professions, inventory, crafting state



Only what addons actually capture



Blizzard APIs



Publicly exposed character and game information



Not a live feed of everything you do



New lightweight addon



Zone visits, session events, custom counters



Must collect events while the game runs



TSM and pricing data



Market prices, inventory and some auction activity



Historical coverage depends on saved records



Local snapshots



Gold and inventory trends over time



Changes between snapshots may be invisible



Manual annotations



Personal goals, milestones, character lore



Requires some intentional input



For instance, a chart showing gold balance over time could be built from periodic snapshots.



But a chart showing exactly how much gold you earned from crafting versus questing versus selling junk would require more detailed transaction tracking.



And a zone-visit heatmap would need a purpose-built addon or another existing source that actually records location history.



This matters because I don't want to build a beautiful dashboard that quietly invents data it doesn't possess.



Here's where I think your idea becomes genuinely powerful

I wouldn't start by choosing Grafana, Airtable, Baserow, or any other frontend.



I'd start with a Warcraft Telemetry Catalog.



Not a formal specification. More like an ever-growing collection of things we could measure.



Each idea gets four attributes:



Interest: Is it useful, entertaining, or simply weird?



Availability: Do we already have the information?



Collection difficulty: Would it require a new addon, an API, or additional local processing?



Historical value: Does it become more interesting after weeks or months of observations?



Then we experiment.



Some ideas will turn out to be boring once visualized. Others will unexpectedly become your favorite widgets.



And we should be perfectly willing to delete the boring ones.



That's the beauty of making a personal dashboard. It doesn't have to satisfy anyone else's definition of useful.



One idea I'd especially love to explore

The DuckMoo Warband Time Machine.



Imagine being able to select a date and see what your entire warband looked like then.



How much gold did you have? Which characters existed? What professions had they developed? Which recipes were known? What were the material prices? How had your crafting capabilities changed?



Then compare that with today.



That requires historical snapshots, which your current application may not preserve beyond its latest imported state. But it wouldn't necessarily require changing the core crafting calculations.



It could eventually become a separate historical data collector consuming sanitized exports from Crafting Desk.



And now your dashboard isn't merely showing the state of your Warcraft empire. It's showing how that empire evolved.



That's a genuinely different experience from Wowthing or a conventional crafting calculator.



I think the important thing is not to turn this into another 15-feature development plan yet. You're still exploring the concept, and that's where the fun is.



But I do have one question that might help me understand the vision in your head:



When you watch those homelab dashboard videos, is the part that makes you go "I WANT THAT" primarily the visual spectacle of having dozens of beautiful, constantly updating charts and widgets, or the ability to discover relationships and patterns in data that you otherwise wouldn't have noticed?



Because I suspect your ideal Warcraft observatory involves both, but the balance between them would tell us a lot about what to explore first. 🦆💜



User attachment



Pasted text(2).txt

Document

i have an addon called Journalator that already tracks a LOT of that stuff, at least as far as money

OH! Journalator changes the equation considerably. 😂💜



You've already got a financial transaction recorder sitting inside WoW, and the screenshot shows something much more interesting than a simple gold counter.



Journalator is tracking crafting orders with the item, profession, customer, crafter, timestamp, and money received. It also has sections for the Auction House, vendors, questing, looting, mail, and trades.



And you included an actual CSV export!



That means the Warband Observatory wouldn't necessarily need a new addon to collect its financial history. We could potentially use Journalator as an existing source of transaction data.



There's a particularly exciting distinction here:



Crafting Desk tells you what should be profitable. Journalator can help tell you what actually happened to your money.



Put those together, and we could eventually compare forecasts against observed financial activity rather than just making prettier versions of the same charts.



I took a look at your actual export

JOURNALATOR · CRAFTING ORDERS EXPORT



Recorded orders



1,681

Gold received



113,780g

Crafters represented



17

Professions



8

September 9–October 19, 2026. Gold received is not net profit; the CSV doesn't include the cost of materials consumed.

Orders by profession

0

150

300

450

600

Alchemy

Inscription

Tailoring

Jewelcrafting

Engineering

Leatherworking

Enchanting

Blacksmithing

Alchemy: Orders 440

Inscription: Orders 314

Tailoring: Orders 276

Jewelcrafting: Orders 197

Engineering: Orders 179

Leatherworking: Orders 126

Enchanting: Orders 75

Blacksmithing: Orders 74

Counts from the uploaded Journalator CSV



That's an average of roughly 42 recorded crafting orders per day over the covered period. And 1,675 of the 1,681 entries are patron orders.



You already have enough historical data for genuinely interesting visualizations:



Which characters complete the most orders.



Which professions generate the most recorded income.



How crafting activity changes over time.



Which recipes you fulfill repeatedly.



Whether different characters specialize in different kinds of orders.



And this is only the Crafting Orders export. We haven't even examined the Auction House or vendor histories.



The exciting architectural possibility is that Journalator becomes the historical financial record, Crafting Desk becomes the planning engine, and the Observatory becomes the visualization layer.



One technical caveat: the CSV gives us transactions, but we'd need to inspect Journalator's SavedVariables structure before deciding whether Crafting Desk could import the history automatically. We'd also need to avoid counting the same money twice when combining records from different sources.



But you've just answered one of the biggest questions about your dashboard idea: Where would all this historical financial data come from?



Apparently, quite a lot of it is already sitting on your computer.



And now I'm very curious what the Auction House export looks like. That's where this could start getting spectacularly ridiculous. 🦆💜



The Auction House data can become enormous.

If you store every individual auction listing every hour, the database could grow very quickly, especially with region-wide commodities.

For a personal observatory, I'd initially store aggregated snapshots per item and market, such as minimum price, total listed quantity, number of listings, and price distribution.

That preserves a tremendous amount of analytical value without needing a miniature data center.

And none of this requires public hosting. The collectors, database, and Grafana can all run on your own computer, with optional access from your laptop on your home network.



The part that makes me especially enthusiastic is that this doesn't have to interfere with finishing Crafting Desk.

Crafting Desk remains your operational tool. The Observatory becomes a separate, read-only analytics system that consumes its data alongside Journalator and Blizzard's API.

So yes, you've moved from "I like those cool homelab dashboards" to an entirely plausible architecture for building one.

And somewhere in the future, Grafana will solemnly inform you that your Arcanoweave Reagent Rucksack Empire is experiencing a 37% increase in market disappointment.

Which is precisely the sort of vital business intelligence the DuckMoo Media Empire deserves. 🦆



















&#x20;   













1 selection

this is how TSM tracks sales and volume/sale rate. they pull the data every 15 minutes then their server compares one data set to the previous one to determine what sold and what is new and all that. combine that with things like journalator and auctionator from local files and you get a pretty comprehensive view of the AH.



























YES! And that's the missing piece that makes this much more interesting than a conventional Auction House dashboard. 😂

You're describing a system that combines market-wide inferred activity with your own directly observed transactions. Those are two different kinds of evidence, and putting them together is where the magic happens.

The important distinction is that TSM-style snapshot comparisons don't prove exactly what sold. They estimate market activity based on what disappeared between scans, accounting for what they can about new listings, expirations, cancellations, and relistings.

But that's still extremely valuable data.

The three layers of Auction House intelligence

Source	What it contributes

Blizzard API	Market-wide listings, prices, quantities, supply changes, and estimated sales activity

Journalator	Your actual purchases, sales, auction failures, deposits, and other gold transactions

Auctionator / TSM local data	Local price observations, scan history where available, market statistics, and additional item context

The interesting thing is that these sources can cross-check one another.

For example, imagine tracking a particular crafting reagent.

Example: Thalassian crafting reagent

Illustrative data



12:00 PM

18,400

Units listed



12:15 PM

15,900

Units listed



Net change

\-2,500

Units of supply





A 2,500-unit decrease is evidence of reduced listed supply, not proof that 2,500 units sold.



Now combine the evidence:

\- API snapshots show how the market changed.

\- Journalator confirms what you actually bought or sold.

\- TSM provides historical pricing and sale-rate estimates for comparison.

\- Crafting Desk can calculate whether producing the item is worthwhile at those market prices.



And here's where it gets especially useful: you could eventually compare TSM's estimated regional sale rate against the market behavior your own collector observes.

Not necessarily to replace TSM, but to see whether its estimates agree with what your particular market is doing.

There's an even bigger opportunity here

Instead of merely storing hourly market summaries, the collector could retain enough listing-level information to compare snapshots intelligently.

That allows us to distinguish:

\- New listings: auctions that weren't present in the previous snapshot.

\- Disappeared listings: auctions that were present but no longer appear.

\- Continuing listings: auctions still present, potentially with updated quantities.

\- Price movement: changes in asking prices and the available supply at each price.

\- Observed sales: transactions confirmed by Journalator for your own characters.

For realm-specific auctions, stable auction IDs can help track individual listings. Commodities require more careful treatment because aggregate quantities and listing representation don't necessarily provide a reliable identity for every unit.

We'd also want to preserve the difference between estimated market activity and confirmed personal transactions in the database.

The truly ridiculous part: historical intelligence

Once the database has been collecting for months, Grafana could answer questions like:

"Do material prices consistently rise on raid reset days?"

"Which items have high apparent turnover but terrible profit margins?"

"How often do I buy materials immediately before their prices drop?"

"Does my crafting income correlate with market-wide demand?"

"Which profession actually generates the most gold relative to my concentration expenditure?"

And my personal favorite:

"How much gold have I lost to stubbornly refusing to stop posting things that nobody wants?"

We could even build a DuckMoo Market Confidence Index, combining estimated turnover, price volatility, listing competition, historical sale rate, and your own transaction success.

Not as some magical prediction engine, but as a transparent score where every component is explainable.

One architectural detail matters here: the Blizzard API doesn't guarantee a fresh snapshot every 15 minutes, so we'd record the API's actual update timestamp and avoid treating identical responses as new market observations.

What you've described is essentially a miniature version of TSM's market-data infrastructure, except with an extra advantage: it knows your own characters, inventory, crafting capabilities, actual transactions, and decisions.

That's a lot more interesting than simply copying TSM's charts.

It's a personal Azeroth economic observatory, and I think the combination of Journalator's confirmed transactions with market-wide historical snapshots is the foundation that makes it genuinely useful rather than just pretty.



















&#x20;   













now imagine that level of degenerate data keeping. but for everything. not just gold/economic data. every possible metric imaginable, all tracked and filed away because when your info isnt on a cloud provider or external server, megabytes to a couple gigabytes of storage isnt really that large when the system has a 1TB drive in it and isnt trying to hold the entire everything in memory, instead just searching for what it wants :) obviously im being a little extreme in that example, but you get my point. i could have the part that reads all my game info on my desktop, and have it sending to a mini pc running some flavor of linux with the database and docker and API grabbing and all that. and then even more extreme unhinged, in the future could have a local ai model set up to mine the database if i wanted to ask random questions about anything











&#x20;















Okay, now we're getting somewhere. 😂💜

You've essentially described a self-hosted observability platform for your entire existence in Azeroth.

Not a character dashboard. Not an Auction House tracker. Not even a warband manager.

A personal World of Warcraft data warehouse, where absolutely everything that can be measured gets recorded, timestamped, indexed, and preserved because why wouldn't you?

And I think the most important thing you just said is this:

Storage is cheap. Information you failed to collect yesterday is impossible to reconstruct tomorrow.

That's the philosophy I'd build this around.

The DuckMoo Warband Observatory

Windows Gaming Desktop



WoW · SavedVariables · Journalator · Auctionator · TSM · DuckMooCapture

Local collector watches files and sends changed records



Home LAN



Linux Mini PC



Docker

Services \& collectors





PostgreSQL

Permanent history





API Workers

Blizzard snapshots





Grafana

Visualizations









Future Local AI



Natural-language questions → safe database queries → answers and charts







Any Browser on Your Home Network

Grafana · dashboards · historical explorer · AI chat





And there's a subtle architectural decision here that I really like.

Your gaming PC doesn't need to do the analysis.

It just collects information and ships it to the mini PC. The mini PC handles the databases, indexing, API requests, scheduled jobs, and Grafana queries.

That means your WoW computer can be turned off while the mini PC continues collecting external information.

What does "everything" actually mean?

This is where I'd stop thinking in terms of individual dashboards and start thinking in terms of entire categories of historical knowledge.



Combat and gameplay

Kills, deaths, damage, healing, dungeon runs, boss encounters, difficulty, duration, wipes, and performance trends. Combat logs could provide especially detailed encounter data when logging is enabled.









Professions and crafting

Recipes learned, specialization changes, knowledge progression, concentration, resourcefulness, multicraft, actual crafting outcomes, production costs, and historical profitability.









Inventory and collections

Bag contents, bank and warbank holdings, inventory changes, mounts, pets, toys, transmogs, achievements, and collection progress over time.









Exploration and activity

Zones visited, quests completed, reputation gains, travel patterns, time spent in different activities, and how your gameplay habits change across expansions.









Warband sociology

Which characters get played, which ones get neglected, how resources move between alts, which professions support which characters, and who actually contributes to the warband economy.







Obviously, not every one of these metrics is already available. Some require additional addon instrumentation, some need combat logging, and some may be restricted by Blizzard's addon API.

But that's a data acquisition problem, not a fundamental problem with your architecture.

And we wouldn't need to capture every metric at the same frequency. Character inventory might be snapshotted on login/logout or relevant changes. Market data could follow Blizzard's update cadence. Combat logs could be ingested after each session.

The part I'd really insist on: never throw away the originals

I'd use three levels of data storage.

Layer	Purpose

Raw archive	Preserve original source snapshots or event files, compressed and timestamped

Normalized database	Extracted records with consistent character, item, event, and timestamp identifiers

Derived metrics	Calculated statistics, trends, comparisons, and Grafana-friendly summaries

This is important because future-you might invent an absolutely unhinged question that present-you never anticipated.

If we only stored today's calculated metrics, the underlying information needed to answer that question might be gone.

If we retained the original data, we could simply write a new analysis and process the history again.

For storage efficiency, unchanged files wouldn't need to be archived repeatedly. Content hashes and deduplication would prevent that.

I'd also give every record its source and import timestamp, so we can distinguish when something happened from when the observatory learned about it.

And I'd keep sensitive or private game data, particularly chat and information about other players, out of broad collection by default.

And then comes the local AI. Oh, the possibilities.

This is actually one of the more sensible applications for a local language model.

Not because you'd need an AI to calculate averages. SQL does that perfectly well.

But because you won't always know what question you want to ask until you think of it.

Imagine opening your Observatory and typing:

Which of my characters has been the most economically productive over the last six months, after accounting for materials bought by other characters?



Or:

Which zones do I spend the most time in, and how has that changed since Midnight launched?



Or:

Find me three statistically interesting things about my warband that I probably haven't noticed.



Or the truly essential question:

Which character is the biggest freeloading little goblin in my entire warband?



The AI could translate those questions into read-only SQL, query the database, perform comparisons, and explain the results.

For reliability, I'd have it show its sources and calculations, and distinguish measured facts from inferred conclusions. A small local model could be useful for query generation and explanation without having to load the entire database into its context.

That's the key: the model doesn't need to remember your millions of records. It needs to know how to ask the database for the relevant ones.

Your 1 TB drive stores the history. PostgreSQL indexes it. Grafana visualizes it. The AI interrogates it.

And the database can keep growing for years.



There's also a lovely consequence of this architecture: the Observatory can outlive individual addons.

Suppose Journalator stops being maintained in three years. Your historical Journalator data is still in your database. A new addon can become the source of future transactions without erasing the old history.

Same for Auctionator, TSM, Crafting Desk, or anything else.

You'd be building a permanent historical record of your Warcraft life, independent of whichever addons happen to exist at the moment.

And that opens up one particularly ridiculous possibility.

Imagine it's 2031. You open Grafana and ask:

"Show me how my playstyle evolved from The War Within through the next three expansions."

And instead of relying on vague memories, you've got years of actual evidence.

That is a level of data-hoarding degeneracy I can absolutely get behind.

One question, though, because it would shape the entire philosophy of the system: Would you want the Observatory to eventually track everything happening across all your WoW clients (Retail, Classic, Forever, etc.), or would you keep it strictly Retail initially and expand later?



\# Introducing Project M.O.O.

\*Because apparently I can't just play World of Warcraft like a normal person.\*



So, I've decided that simply having 47 different addons, a crafting management application, and an unhealthy obsession with collecting things isn't enough.



I'm building my own \*\*self-hosted World of Warcraft data intelligence platform\*\*.



And when I say data intelligence, I mean an absolutely unreasonable amount of data.



\*\*The basic idea:\*\*



Imagine something like TradeSkillMaster, Warcraft Logs, a character history tracker, Grafana, and a tiny personal Palantir all had a very questionable child.



That's what I'm building.



The system will collect information from my WoW clients, including Retail and the upcoming WoW Forever, combine it with information from addons like Journalator, Auctionator, and my own custom tools, and store it all in a permanent database running on a dedicated Linux server in my house.



We're talking things like:



\- Auction House transactions, market prices, supply, and estimated demand.

\- Gold earned and spent across every character.

\- Professions, crafting, inventory, and resource usage.

\- Quest progression, achievements, collections, and character milestones.

\- Gameplay sessions, dungeon runs, combat information, and activity history.

\- Historical changes across characters, expansions, and even different versions of WoW.



Basically, if the game makes information available and I can reasonably collect it, I want to keep it.



\*\*Why?\*\*



Because storage is cheap, and information you didn't collect yesterday is information you can't analyze tomorrow.



Instead of relying on addons to remember things forever, I'll have a centralized database that preserves the history independently of whatever addon originally collected it.



And because it's all self-hosted, I'm not paying some cloud provider to store years of my own gaming nonsense. I've already got the hardware sitting here.



\*\*The hardware and software:\*\*



The server is a repurposed machine with an Intel i3-10100, 32 GB of RAM, and a 1 TB NVMe SSD.



It'll run Ubuntu Server, Docker, PostgreSQL, and Grafana, with additional services collecting and processing the data.



My gaming PC will handle reading the local WoW files and sending updates to the server. The server will handle the database, API requests, historical analysis, and dashboards.



\*\*Now here's where it gets completely unhinged.\*\*



Eventually, I want to be able to ask questions like:



"Which character has earned the most gold over the last six months?"



"Which crafting materials tend to become more expensive on certain days?"



"How has my playstyle changed between Retail and Forever?"



"Which of my characters is the biggest financial liability to the warband?"



And have the system actually query years of historical data to answer them.



I'm even considering adding a local AI model that could investigate the database and find interesting patterns without me having to write SQL every time I have a ridiculous question.



\*\*But my favorite idea is for Hardcore.\*\*



When WoW Forever eventually gets Hardcore servers, imagine being able to record a character's entire life.



Every level. Every quest. Every major accomplishment. Every dungeon. Every memorable moment the game lets me capture.



Then, when that character's adventure ends, the system could reconstruct their entire journey, identify the highlights, and help create a documentary-style YouTube video celebrating their life.



Not just a death clip. An actual biography of a character's adventures, built from the historical record.



And that's only one possible use.



\*\*The plan:\*\*



Get the basic Retail data collection and dashboards running by the beginning of November, expand into Forever when it launches November 4, and keep adding new sources and increasingly ridiculous analysis features over time.



The important part is building the data collection system now. We can invent new ways to analyze the information later.



Is any of this necessary to play World of Warcraft?



Absolutely not.



Am I going to do it anyway?



\*\*Of course I am.\*\*



Welcome to Project M.O.O., where no crafting reagent goes uncounted and every character gets a permanent file.



\*The DuckMoo Media Empire's Department of Completely Unnecessary Statistics is now accepting applications. There are no openings. We're just collecting your information.\* 🦆

