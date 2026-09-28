# Lauren: how I shipped 2,500 PRs last month

Source: https://x.com/poteto/status/2102050467505430555
Caption source: X English VTT, 882 cues.
This is a complete caption-derived transcript. It is not a manually verified verbatim transcript.
Time labels mark the first cue in each 30-second block; see the TSV for cue-level timing.

## 00:00:00

Hi, my name's Lauren You might know me as Potato on X and I work on Grokbot at SpaceX AI So last month, I did something pretty crazy I shipped 2,000 pull requests to production A lot of how I'm able to do this is through trust and I think a lot about trust in terms of how I can trust my agents to produce high-quality work even when I'm not there

## 00:00:30

And my argument and thesis for this talk today is that if you set up your environment for your agents really really well you can end up with something that looks more like a personal or even team software factory where you're producing very high-quality code at much greater rates than before but I'm not a fan of the term software factory

## 00:01:00

I like the analogy of the Michelin kitchen better where, you know, as technologists, we're not really producing we're not mass producing a product on an assembly line but the work that we do looks very creative It's very, you know, it's the act of building a product and it's art in some sense So, you know, even though with agents we're not cooking the individual components that go into the product anymore

## 00:01:30

we're still responsible for the final outcome and thinking about our kitchen setup Right, because depending on how you set up your line cooks your sous chefs, you know, the kind of equipment they have the kind of training they have you know, dishwashers and the ratio I guess, of line cooks to dishwashers all of these ingredients go into making the final product and I think this analogy is really apt

## 00:02:00

So I wanted to talk a little bit about a story before we begin where six months ago when I first joined Cursor before we were a part of SpaceX AI I obviously had, you know, no agent skills to to use, right? I just joined the company It was a fresh code base and a fresh product that I was working on So at the time

## 00:02:30

Cursor was building the replacement for the Cursor IDE which is the new agents window And, before I joined the Cursor agent window had quite a lot of performance issues and my manager at the time asked if I was able to help them and since I had spent some time on the React team before I joined Cursor it seemed like a good fit but when I first started

## 00:03:00

I quickly realized how manual this process was obviously I have done performance work before but at the rate at which pull requests were being landed it was just it felt almost an insurmountable wall of pull requests that just kept coming in and I had no idea whether or not the performance of the app would be regressing right? So a lot of my early time on the cursor team was spent looking at

## 00:03:30

Chrome DevTools and the performance and doing performance traces and taking heap snapshots and it was extremely extremely manual It wa- it, it was so manual it, it got to the point where I just got really frustrated and started to think about you know, wait, we have agents what am I doing? And so I started thinking about verification skills where, you know what if my agent could actually run the application itself and take the traces for me

## 00:04:00

understand the traces, and find the hotspots and basically hill climb you know, to, better performance in an application automatically And throughout the last six months of being at Cursor and SpaceX AI you can really see that my product really has skyrocketed And, you know I never set out to ship 2,000 pull requests a month That was not a goal of mine at

## 00:04:30

all But I realized that all of the skills all of the tools and and code-based changes I were making laddered up to this idea of trust You know, I didn't know it at the time but, I had this thought in the back of my head head, which was, you know, I am the bottleneck and I need to be able to take all of the knowledge that I have as an engineer and impart them into into my team of agents so that I didn't need to

## 00:05:00

be the blocker for everything And you can clearly see that it's it's paid off So I think it really comes down to trust but how exactly do you build that trust? And where do you start if you're you know wherever you are in your journey of using agents? So, when I started, obviously I was in this category

## 00:05:30

you know, in the one to one to five range where, you still feel like you have to babysit every chat and, and conversation, and you're just constantly course correcting you know, you're intervening you're correcting your agent so that it does the right thing and if you're not there basically nothing gets, nothing happens and the agents do the wrong thing And I would actually argue that this part

## 00:06:00

this phase of, you know using agents is actually the hardest to get out of because it's not always very clear how exactly you get out of it And, again, it just comes down to trust you know, the reason you're unable to go from one one or one to five agents to something more like a hundred is because you don't have trust in your agent's work yet So if you don't have trust and you try to spawn a hundred sub-agents or cloud agents

## 00:06:30

you're going to quickly find that you're just going to get a ton of slop pull requests and you know a bunch of regressions and a bunch of bugs ship and no one's going to be very happy with that So that begs the question how do you trust your agents more? So for me, it came, it, it really started when I like I said, I meant I joined the cursor team

## 00:07:00

and I was starting to work on performance where I realized the need for verification So when I say verification there are sort of levels to that because, you know, on the, I guess the lower end of the scale for verification you have things like the verification skills that I talk about where you teach your agent how to run your application you know and use things like the Chrome DevTools protocol or whatever other protocol that you have for debugging

## 00:07:30

and teach them how to you know, debug the application take performance traces Take heat snapshots and so on and then on the opposite end of spectrum of the spectrum, which is much much harder and still very much an open question is like more formal verification where, you know, maybe you rely on formal methods or, you know languages like Lean or TLA+ to do

## 00:08:00

you know, verification so that you can check that you know, your business level or business logic invariants are, you know, are always, true, and that you can formally verify that your application is always in a correct state but I would say that you know, even if you don't have the ability to run formal methods

## 00:08:30

and very few people really do that with verification skills you can get very far So when I joined Cursor and started to work on the Cursor agent window the first skill that I built was a skill called Control Glass which is a verification skill that teaches the agent how to run the application and take traces like I mentioned and it does that through the Chrome DevTools protocol

## 00:09:00

something interesting about that skill is and I kind of iterated my way to this it didn't start out this way but the control the control or verification skill really has two components to it the first part is obviously a CLI so you want your agent to be able to reproducibly be able to run the application and collect

## 00:09:30

traces and collect evidence that you know, empirical evidence that, you know, code is working that your performance bar is being met and rather than have your agents create scripts every time you know, that can differ between agent sessions you can actually you can actually create a CLI that's within the skill directory and then your agents will just use that every time And then Of course

## 00:10:00

you need to actually invest in it and make it good so that it can handle all sorts of different use cases and, be able to, you know, run the application, correctly another thing that's also really important is this idea of a feature map So a feature map really is something that I kind of coined I guess, where, you know we started using these control skills within cursor

## 00:10:30

Then we quickly realized that you know a Slack report would come in and a user would post a very vague screenshot right? Like a very small slice of the UI and just like three question marks And the agents using our control skills are just no idea Like it could run the application but it would just be guessing at what exactly the the user meant And so I had this idea to create something called a feature map which is I guess kind of inspired by like a

## 00:11:00

sitemap it essentially is a form of materialized memory you know like how exactly does your application work? What features does it have? How do, does a user reach it? you know in terms of like keyboard shortcuts or what DOM elements to click on you know, things like that and what all the fe- different features do and, they are these this feature map is stored in the skill itself

## 00:11:30

in the code base as part of the skill directory. And we have an automation that maintains this feature map as well But when we combined the CLI and the feature map we quickly realized that this combination was very very powerful because now agents can not only you know, reproducibly control the application and take traces but it could also understand requests that came in from internal users as well as external users

## 00:12:00

And so we very quickly realized that the control verification skills were so useful that they've become more or less critical infrastructure for our team and we constantly, maintain it But the ability for an agent to verify its own work is extremely powerful and, we have spent a lot of the time on this skill and it's very very powerful for building that trust

## 00:12:30

in addition to verification of course, you want because ver- verification is really about correctness Correctness to me is really about does the thing does the feature or code do thing that you want it to do? Right, like does the, you know, the checkout button does it actually check out the car? verification is really important for that because you could get empirical evidence that

## 00:13:00

this feature actually works But it doesn't tell you much about you know, the performance or the code quality of that feature and that's where you start thinking about skills that teach agents to work like real software engineers So I've built a plugin called PStack I'm not going to talk about the plugin too much today but, a, a lot of the inspiration for that plugin

## 00:13:30

which is a collection of skills that I've created are inspired by the kind of workflows that I personally have used as my in my time doing software engineering for all sorts of different types of tasks So debugging, you know, feature development, prototyping there's a whole bunch of different playbooks and skills that ship in PSNAC that teach your agents how to write code the way that you want them to

## 00:14:00

And, you know, this is where you know the more experienced engineers on your team can really contribute to set up a team repository of skills that just make your agents a lot smarter And when you combine those skills with verification skills, then you you're able to get to a point where your agents are able to not just verify that the work that they're doing is correct

## 00:14:30

but that it's also high quality And again, because of verification, you can collect real performance metrics you can get real numbers and statistics and telemetry on the, like, performance of the application so I think that's a really important part to invest in another thing I think is really important is refactoring and rewriting your architecture

## 00:15:00

to be more agent-friendly and I almost want to say that this is one of the most important things you can do as a, as a software engineering team because if you really truly believe that agents are going to be writing all the code in the future then we need to design our code bases so that they do the right thing by default And you'll find that there's this I, I almost want to say like a a scale or a continuum between

## 00:15:30

you know, these different pieces of building trust in your agents where, on, you know I have like five of these points here where The code base is really like the best form of memory because agents love to extend existing patterns that they see and, you know I think this is just the nature of how LLMs work

## 00:16:00

where they're more likely to use whatever it is in their context window to make changes And of course the files that the agents read and opens are part of its context window and therefore the code base is a really important part of that because, you know agents aren't gonna just refactor your code every single in every single PR They're gonna just look at what's already there and just extend The next level, I think, is about static analysis

## 00:16:30

where you have linters you have compiler diagnostics you have, continuous integration and these are Guidelines and constraints that you can enforce in your codebase so that whenever you correct your agent you find that, you know they just keep making the same mistake you can add those as lint rules or even better you can refactor your code base so that

## 00:17:00

the mistake that the agent is making becomes categorically impossible and then a step above that right, where, where and this is where we're starting to get more into less of like a hard constraint and enforcement and more into the realm of guidance You have things like rules you have bug bot you have skills, which, you know your agents will obviously sometimes and mostly use when they're doing their work but there's also a chance that it might

## 00:17:30

for various reasons, you know forget to read a rule or maybe the user that is piloting the agent ignores them so these aren't quite as enforceable but also an important part of setting up your environment so that you can really trust what your agents are doing and then finally you have the style guide which is really only enforceable by humans in a code review I guess you could put the

## 00:18:00

put these in your rules and and bug bot and skills as well But if you don't then you have this big glaring hole in your review process, where now humans have to you know look at every single line that's being changed and remember to comment and with the rate of pull requests that are coming in it just, it just becomes impossible So I definitely wouldn't recommend you know, relying only on the style guide I think the style guide or, you know like looking at human reviews is a good place to start

## 00:18:30

in terms of what's missing But you should really invest the time to think about the other four parts you know, your code base making things categorically impossible through better data structures or algorithms static analysis and then of course you layer That with rules and bug bot and skills on the code base front

## 00:19:00

and in the Grokbot code base we actually have invested into setting something up that we call Dune which is our agent-friendly framework So the inspiration for Dune really came about from a lot of performance issues we're seeing we were seeing in the cursor agent window And so a lot of lessons came out of that inspiration but the key principle that we landed on is really

## 00:19:30

that agents love taking shortcuts So what if we design the framework such that the shortcut you know, the easy path is the right path for agents and also one that would be a code base that is you know, maybe pretty annoying for humans to work in because it's so locked down in terms of what you can do and what you can't do But, it actually creates the perfect environment for agents

## 00:20:00

especially ones that have very minimal context because, you know not every contributor to your code base is going to be an engineer anymore You can have designers you can have product managers you can have CEOs you know, going into the code base and and shipping features So we want to really think a lot about how we invest and set up our code bases so that you know even agents that are piloted by busy people with not a lot of context can do a good job by default

## 00:20:30

And like I mentioned before Your code base is really a form of memory for agents because they love to extend the existing patterns that they see And the reverse is actually also true right? You can invest the time to set up your code base in a way that things are you know, bad patterns are categorically impossible or you have, like lit rules that prevent them But the reverse is also true in the sense that

## 00:21:00

if you have existing anti-patterns you'll actually find that these will spread kind of like a virus where you have, like one small workaround or a comment that explains a workaround And you'll quickly find that agents just love to copy that And then in a matter of a few days or a few weeks you'll find that that workaround has spread everywhere and it's now becomes it has become like a de facto pattern

## 00:21:30

for all agents. And that's a really really bad place to be to be in And that goes back to what I was saying about why it's really important you know, whenever you're correcting your your agents that you invest the time into thinking about code base changes and static analysis to and, and of course, the layering them with rules good rules and bug bot and skills because of, of that reason and another analogy that I like

## 00:22:00

in addition to the Michelin kitchen is this idea that you know, your code base is kind of like a garden where you have, workarounds, you know, that seem seemingly that seem kind of innocent at first then because of the nature of agents you just copy that pattern over and over again and you quickly end up with a very you know, vibe-coded code base that is you know a pain in the butt to maintain

## 00:22:30

and has a lot of performance issues So in my opinion the perfect agent code base is one that's so locked down that you know, it, again, it's like really annoying for humans to to write code in but it's so conventional it's so standardized that you know, even innocent-looking patterns are just forgotten and the best example of this I have Is actually something that seems very very innocent when you look at it

## 00:23:00

but when you think about it it's actually really bad And that pattern is agents leaving comments in the code Now, you know when I first saw agents starting to do this I initially wasn't, well, I I did think that a lot of them are slop but I also thought that you know, it actually doesn't, it's, it's not a bad thing right, I guess, if agents are leaving comments in the code because as humans we left comments in the code whenever we saw you know, edge cases or we needed to actually make a workaround

## 00:23:30

or, you know, leave a note to ourselves or a a colleague on a particularly tricky part of the codebase But What I quickly realized when we saw this happening in the cursor codebase was that agents were just using the comments around the code as justification for why it wasn't going to solve the actual problem and instead paper over it with a band-aid or a short-term solution

## 00:24:00

So, in Dune, which is again the framework that powers Grokbot we made the choice to we made the choice to actually ban comments for that reason where, so that agents would not just copy that pattern and you know, propagate it everywhere in the codebase So

## 00:24:30

my pitch here is that every team really needs something that you know, a role that I'm calling a gardener in the same way that you know, with a real garden you need someone who is thinking a lot about the you know things that can kind of creep in and grow in ways that you don't want Like, you know, you have weeds, you have, you know just other types of organic growth I don't really know gardening that well

## 00:25:00

but you have things that you know, unwanted pests and, and stuff like that that kind of creep in in hierarchical based And so you want to nip them in the bud as soon as possible before they start propagating everywhere a lot of the principles behind Dune are really centered around these three things First of all we want to delete tech debt that we already have for you know, for reasons I just mentioned We want to keep or enforce a single paved path for most

## 00:25:30

blessed patterns you know there should be one conventional way to do some things so that agents don't really need to guess and there should be enough guidance in the codebase in CI, in lint rules so that the agents are guided to do to, to follow that path And then finally, whenever you see tech debt or bad patterns your instinct should be I need to write a lint rule against

## 00:26:00

it. You don't always have to clean it up immediately because if you write a lint rule you can at least stop the bleeding and which, you know, doesn't solve the problem entirely but it at least prevents it from growing so I definitely recommend you know really thinking a lot about how you can guard against anti-patterns so that they don't spread like a virus and then also spend time to actually you know get your agents to clean them up so

## 00:26:30

that your code base is just constantly kept in a state where you would be happy if an agent were to copy it That's the kind of mindset that I would recommend having and then I won't actually go through all the details of Boone itself but I'll just kind of gloss through some interesting parts so again, as a reminder, Boone is the architecture the client framework that we built to power Grokbot We've invested a lot into you know, all the things I was saying where we have

## 00:27:00

conventions. We have a lot of conventions about where code should live and where and how code should be imported between them So in dune applications you know, there's different concepts where like, for example features are all co-located in a single folder you have an entry point that's, you know in the React part of the code that determines or you can kind of think of it like a route you have transcript pods that

## 00:27:30

show up in the GraphBot application You have a host that runs on the you know, the GraphBot virtual machine And then, of course, you have your client which, powers the, overall dune application And we have a lot of strict boundaries between these things where Just as an, as an example things that run on the main process or the main thread in Electron aren't allowed

## 00:28:00

to be run on the renderer thread and we keep that separation very intentionally because of lessons we learned from Cursor's agent window where we would sometimes see code accidentally get imported into the renderer thread and you know, slow code, and, since on the renderer thread you want your UI to be very smooth and performant you need to make sure that you don't have any long tasks or you know, things that take longer than 16 milliseconds

## 00:28:30

or if you want like, 60 frames per second or 8 milliseconds if you want 120 frames per second. And so your renderer has to be constantly in a state where it is, it can really kind of chunk up the work and not do them all at once and so we have code within Dune that enforces this these boundaries through the import

## 00:29:00

dependency graph but yeah that's just an example of a pattern that we saw lead to really bad performance that we categorically eliminated through, the architecture of the of Dune and then all of these other pieces aren't that interesting but again, the, the core theme here you know, it's not about Dune but the idea that

## 00:29:30

An agent-friendly framework of your own is actually very very powerful and it can encode all of the learnings that you and your you know your best engineers on your team have tribal knowledge of and I think the lesson here is that how do you take that away from you know what used to be in the style guide process of reviewing code and you know, engineers reviewing other engineers' work and leaving comments

## 00:30:00

to extract almost like extracting that knowledge and encoding that into the framework into the code base itself so that the code base access the memory right? It's the, the thing like you're coming back to this idea that you know the code base is just the thing that it's the the materialized snapshot of the state in which you want your agents to extend and you want that code base to be so pristine so great that

## 00:30:30

the next agent that comes Is just very likely to continue that pattern and keep it really really good and if you spend enough time on this process like I mentioned, you can really set up a Michelin kitchen or a software factory where because you've spent so much time on you know all of these pieces that allow you to trust your agents whether it's in the code base whether it's lint rules

## 00:31:00

whether it is, you know diagnostics or rules or bug bar or skills these layers come together and provide you a lot of trust Because now, you know just imagine for a moment you're working in the Grokbot code base It's super locked down you know, it's like almost impossible to write bad code So, you know, you can even an agent with very little context

## 00:31:30

you know, even a a agent with not a lot of reasoning can come in and and actually write code that's good And going back to my example about the Michelin factory I think there's a lot here right, where, you know, we're setting up our agents our bots with skills and tools you know, we're training them we're setting up our kitchen in a way that makes sense right for the agent and bots to do the right thing by default you know, whenever we see, for example, in the, in the kitchen example

## 00:32:00

if we notice that one of our cooks or dishwashers is constantly tripping over something of course we need to fix that right? We need to problem solve and ensure that you know, others don't trip as well because you know in a kitchen it's a very dangerous place and you don't want to hurt yourself It's the same Mindset, I think that we should have with our codebases How do we set it up so that even agents without a lot of

## 00:32:30

knowledge can, can do a good job? and I think with you know, Grokbot, Grokbot and Cursor play an interesting role together where Grokbot is really great at providing what I call the outer loop because you can connect Grokbot to lots of different you know, different connectors like Slack to Datadog, Sentry, PlanetScale, whatever services that you use

## 00:33:00

and you can aggregate all of that information together and use that to make really good decisions for itself Some people call this like a company brain I don't really think I personally don't think you need anything that sophisticated here because agents are really good at using tools And so if you connect these tools to Grokbot and you start having your Grokbot's auto kick off things like cloud agents you can actually find that it's really not

## 00:33:30

you don't really have to invest in a lot of infrastructure to build a software factory in fact, I'm gonna, you know, cross, cross out this this term, cause I don't like this term I think you can set up this personal Michelin kitchen for yourself through Grokbot things like Grokbot routines which let you subscribe to you know, Slack threads to Sentry alerts that let you kick off things automatically

## 00:34:00

And when you combine all of these things that I've been mentioning you know, your code base, your rules, your skills, they all compound And GrokBot, will be able to you know automatically respond to events that come from the outer loop and then kick off cloud agents and you can also set up cursor automations and use our SDK to set up, bot additional bots as well that

## 00:34:30

reuse a lot of these pieces of agent infra that you've set up and allow them to do much more complicated tasks So if you, if you, if you've done all this then I think you can get to a point where you know I have some screenshots here of some of our automations and our agents in that, that work on cursor where we are automatically reproducing bug reports

## 00:35:00

we're automatically opening pull requests we are essentially adding a lot of value to the entire team because all of these things compound So if we kind of zoom out again and go back to this graph I think that to kind of close off the talk if you spend a lot of time thinking about all of the pieces that you need

## 00:35:30

to be able to ascend the trust graph you start getting to a place where you can really trust your agents more and parallelize your work and also empower your entire team to build on top of these pieces of infrastructure for your agents and empower everyone, you know, every engineer on your team every builder to be extremely productive and be able to write high quality code

## 00:36:00

So the last thing I want to leave you with is actually this piece sorry, not that piece, but this piece I think if there's only one thing you take away from your talk it should be this this slide here, which is, you know these are the activities that will help you build up towards a high trust environment you know Whenever you find yourself correcting and interviewing your agent you really want to think about it from these five pieces

## 00:36:30

and where is the most effective step in this sequence, in order to, get make your agent you know, much more trustworthy and of course, I definitely recommend thinking about thinking about it in this order where, you know, you either invest the time to make that pattern categorically impossible through your code base and architecture and data structures

## 00:37:00

or you start looking at things like static analysis and then you layer that on with rules and bug bot and skills If you do all of that and you also spend some time you know, thinking about, your code quality in, in terms of, of skills you get to a place where you trust the you trust the environment so much that your agents can just be free right? And, personally

## 00:37:30

I have spent a lot of time for this for Grokbot's codebase, for example, and, this is really the secret right? Well, it's not really a secret it's, it's a lot of hard work but, I hope you found this talk useful and, please reach out to me on X my, my handle is potato with an E and I hope that you'll have a lot of fun and success building your own Michelin kitchen

## 00:38:00

Thanks for watching
