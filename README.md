# afterburner
_One of the faster ways to learn a spoken human language._

You might also be interested in the "Afterburner Cartridge Factory" helper program for constructing afterburner cartridges, which is [here](https://github.com/aleksnavratil/afterburner-cartridge-factory). Note that currently "factory" is a bit of a misnomer, since cartridge construction is still pretty manual.

## What's the point of this program

The point of this program is to teach you to be plausibly conversant in a spoken human language, such as Italian or Polish. This program is substantially an open-source clone/blatant ripoff of [language101.com]'s excellent software. It is designed such that it can work with many languages, but the only one that's built so far is Italian.

## Pedagogical philosophy
Afterburner is Opinionated Software (tm), designed around the idea that there is a right way and a wrong way to learn a language. 

#### Background
Every language learning system works, it's just that some work faster than others. Some systems work so slowly that they're nearly indistinguishable from no instruction at all. Afterburner is one of the faster systems --- but why does it work faster than others?

Many skills can be trained during language learning. Here are some examples of trainable skills, using Italian as the target language and English as the known language.
 
* Reading and comprehending written Italian
* Translating written Italian to written English
* Looking at a picture of an object and writing the corresponding Italian noun
* Looking at a picture of a scene and selecting the correct description from a set of multiple choices
* Filling in the missing words in an Italian sentence, like in the CLOZE exam or MadLibs
* ... etc ... 

There are a large number of these skills; if you spend any time with the common language learning systems such as Rosetta Stone or DuoLingo or whatever, you'll find endless variations on these skills, probably ten or twenty or more. However, it turns out that in practice, almost none of these skills matter. In fact, for becoming passably conversational, only two skills matter:

**Important Skill #1:** Reading written English, and translating to *spoken out loud Italian*.

and

**Important Skill #2:** Listening to and comprehending spoken Italian

It turns out that if you master these two skills, you *get all the other skills for free*. Curiously, many heavily-advertised language learning systems spend zero to five percent of their time training these two skills. And it turns out that your learning rate is almost exactly predicted by the fraction of your time spent training these skills. So as a rule of thumb, most popular language learning systems are wasting ~95% of your time. That's why Afterburner works so much faster than other systems.

The *whole point* of Afterburner is to spend all your study time training **Skill #1**. Note that you *absolutely must say the phrase out loud.* If you just think it in your head, or say it in English, or do anything other than say it out loud in your target language, the magic breaks and you'll revert back down to low-speed language acquisition just like in any other system. 

**Skill #2** is trained by [Yabla](https://www.yabla.com/) which you should use alongside Afterburner or Language101.com.

A consequence of this relentless focus on **Skill #1** is that Afterburner isn't much to look at, particularly if you're used to the shock-and-awe graphics common to many of the heavily-advertised language systems. But bear with it, because it *teaches you a lot* in a short time.


## FAQ

__Q. Maybe this works for you, but you're not at all neurotypical. It won't work for everyone.__

A. True, nothing works for everybody. However, brief and highly non-scientific research suggests that it works for some non-trivial subset of the population. I suspect that this subset is "almost everyone" but I could be wrong.




__Q. Ok, I believe your theory about Important Skills #1 and #2, but why are rival language systems designed around such glaring ignorance/misunderstandings of human language cognition?__

A. They're here to take your money/get their KPI's up, not teach you a language. How do you think they can afford all those shiny ads in Conde Nast magazines? Their business model doesn't depend on you actually learning anything.




__Q. Ok, this looks great. Does it work for my language of interest X, which is written left to write/top to bottom/with super-exotic glyphs or in a very unusual character set?__

A. Ummm. I am probably not smart enough to reason about your vertically-written language. That said, Afterburner is Unicode all the way down, so in general it might be expected to approximately work. However, I make no promises about whether the UI can render your character set in an intelligible vertical order.




__Q. But I'm a visual learner/tactile learner/whatever other BS they taught me in elementary school.__

A. No you're not, there's no such thing. The "learning styles" myth is peristent and sticky but wholly debunked, see e.g. [here](https://www.teachermagazine.com.au/articles/tackling-the-learning-styles-myth) or [here](http://journal.frontiersin.org/article/10.3389/fpsyg.2015.01908/full) or any of the many many other readily-available and very thorough debunkings.




__Q. Your user interface looks like it was built by a small, not very bright child.__

A. Yes, you're right. At some point I might learn how to write a better one. Bear in mind that the point of this program is to display text and play .mp3 files. Rocket science this is not, and a minimal interface kinda suits the application.




__Q. Yes but the flicker is annoying.__

A. You're right, that's why I might built a better UI.



__Q. How is this different from Language101.com's software?__

A. In spirit, it's not very different, other than that their software is slightly more sophisticated than Afterburner and has a couple more features such as progress bars and study stats. The pedagogy and user experience is almost identical. The only substantial differences are as follows:

* Cost. Afterburner is free, most other good language learning programs are not.

* Afterburner is extensible, and it provides more hours of study than Language101. This is the main benefit---it's pretty easy to exhaust the Language101 curriculum for a given language pair. Depending on your study speed, they provide only 30-100 hours of instruction. In general this is around 1/3 of what's necessary to become conversational.

* Afterburner is designed modularly, such that in principle it can work with any pair of languages. Conversely, Language101 supports only a limited subset of language pairs. However, Afterburner currently has curricula only for English-to-Italian, so this is not much of an advantage.

In general, if Language101.com supports your language pair, you should buy it and exhaust its curriculum before using Afterburner. Their lessons are generally better in almost every way --- they have better audio recordings, more carefully-tuned pedagogy, a fancier spaced-repetition algorithm, etc. In fact, Afterburner was only invented as a response to the fact that Language101 doesn't have enough content. So for the language pairs that Language101 supports, the available Afterburner cartridges tend to pick up where Language101 leaves off. 




__Q. So should I buy Language101 or not? It seems kind of expensive.__

A. You should buy it, it's worth every penny. It's hands-down the best available language learning pedagogy on the market. It's better than Afterburner, which is just a poor-man's ripoff of it.




__Q. You sound like a shill for Language101.__

A. Nope, just a satisfied customer who wishes they supported more languages and levels. If I were a shill, why would I clone their software and release it for free? You should also pay for Yabla, to train Skill #2 from above, and I'm not a shill for them either. 




__Q. But I saw a fancy yellow ad for Rosetta Stone, shouldn't I buy that instead!?__

A. I mean, it's your money and your time. But I solemnly promise you will *never* learn your target language to a conversational level by using Rosetta Stone alone. It works so slowly that a single human lifetime is not enough time to learn any language with it. 




__Q. How do you know Afterburner is better than alternative system X, have you tried it?__

A. In general yes, I have tried most of the widely-available language systems out there, including academic classes, Rosetta Stone, DuoLingo, Anki, Fluenz, Language101, etc. Most of them work, but some work faster than others. In general you should find the combination of tools that maximizes your learning rate, and use that toolset to the exclusion of all others. 




__Q. Will Afterburner teach me to write eloquently in my target language?__

A. No, it's for becoming minimally conversational. The idea is to get you to the point where immersion is a time-effective pedagogy. 




__Q. Afterburner made me mostly conversational in language X, but now I'm stuck/plateaued.__

A. Yes, this is a known thing. No computerized method can help you now. You need immersion or at least to Skype with native speakers regularly. Go spend 3 months in a location where your target language is spoken and you'll be fine.



__Q. Are there better methods than Afterburner for language learning?__

A. Yes, I strongly suspect that Afterburner + Yabla + [Total Physical Response](https://en.wikipedia.org/wiki/Total_physical_response) with a native speaker tutor is the *best* available pedagogy, and you should do this if you have unlimited money and time. In fact TPR *alone* might work better than anything else. However, TPR is expensive because you need a human tutor. So in terms of learning per dollar, Afterburner is a better deal. 



__Q. How long does it take to become plausibly conversational with Afterburner?__

A. 100-300 hours, depending on your brain wiring/learning rate. Typically this is spread over 30 or 60 minutes of study per day, with very few or no days off. 



__Q. What's the deal with the "cartridges" thing?__

A. In the 90's, when you bought a Nintendo, you had to also buy some games, which came on little grey plastic cartridges. You could use the same Nintendo console to play many different games, but without the games the whole thing was useless. This is kinda similar --- Afterburner itself is like the Nintendo, and the games are like the different language pair cartridges. So ideally there will eventually be a cartridge file for learning Polish for English speakers, another cartridge file for Portuguese for Russian speakers, etc. Currently we only have Italian for English speakers, but more cartridges are in the works. If you're interested in constructing your own cartridge, you're more than welcome to; the format is very intuitive and transparent. There's also a [method](https://github.com/aleksnavratil/afterburner-cartridge-factory) for transforming Anki card stacks into Afterburner cartridge files, though the legality of doing so probably depends on many factors. Don't break the law. 

The contents of each cartridge file is just a bunch of .mp3's with numerical filenames such as 3465 or 295, with no file extensions, and a .sqlite database containing some text in both the known and target languages. The sqlite db just tells Afterburner which text goes with which audio files. 

You can find the canonical list of available cartridges [here](TODO: FIGURE OUT WHERE TO HOST CARTRIDGE FILES)




__Q. Why are there no study stats, showing e.g. my total study duration?__

A. Will build soon, hang tight. 

## Explanation of the files in this repo

