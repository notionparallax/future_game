---
layout: post
title: A Game About Possible Futures - the cards
date: 2021-1-1 9:00:00 AEST
type: post
published: true
status: publish
categories: []
tags: []
author-name: Ben Doherty

# this goes on the index page, and into facebook shares
description: "A game to help you think about the future."

# This is what twitter will pick up if someone tweets the link to this page
# 110 marker 1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789
twitter-body: "A game to help you think about the future."
# Twitter and facebook will pick up this image. you can also use it in a post with: -
#![alt text]({{ site.baseurl }}/assets/{{page.featuredimg}})
featuredimg: https://fastly.syfy.com/sites/syfy/files/2018/03/silver-surfer.jpg
---

<style>
  @import url('https://fonts.googleapis.com/css2?family=Monoton&display=swap');
  a {
    overflow-wrap: break-word;
  }
  /* body {
    background-color: beige !important;
  }  */

  figcaption {
      float: right;
      border-radius: 0 0 1em 1em;
      border: silver solid;
      border-top: none;
      padding: 0 0.5em;
  }
  figcaption p {
    margin-bottom: 3px;
  }
  .card figure, .card figure p {
    margin-bottom: 0;
  }
  .card h2 {
    line-height: 1;
  }
  .toc {
    column-width: 12em;
    font-size: 70%;
  }
  li img {
      height: 5em;
    }
  @media screen {
    .to-print {
      display: none;
    }
    section.card{
      width: 9in;
      border: 1px solid black;
      border-radius: 1em;
      padding: 10mm;
      font-size: 10pt;
      height: 6in;
      column-count: 2;
      column-fill: auto;
      margin-bottom: 1em;
    }
    section h2,
    section h3 {
      margin-bottom: 0;
    }
    article.post section blockquote {
      font-size: 80%;
      width: 100%;
      padding-left: 0.5em;
    }
    
  }
  @media print {
    /* html, body {
      height: 210mm !important;
      width: 297mm !important;
    } */
    @page {
      /* size: 148mm 210mm !important; */
      size: A5 landscape !important;
      margin-bottom: 0;
      margin-left: 0;
      margin-right: 0;
      margin-top: 0;
    }
    iframe,
    header {
      display: none; 
    }
    .post-content {
      column-count: 1 !important;
    }
    section {
      background-color: white;
      break-inside: avoid;
      column-count: 2;
      display: inline-block;
      outline: 1px solid;
      padding: 1cm 1.5cm 1cm 1cm;
      page-break-before: always;
      vertical-align: bottom;
      height: 148mm;
      width:  210mm;
      position: relative;
    }
    section::before {
      position: absolute;
      transform: rotate(90deg);
      font-size: 200%;
      font-family: 'Monoton', cursive;
    }
    section.technology::before {
      content: "Technology 🤖";
      right: -90px;
      top: 140px;
    }
    section.trend::before {
      content: "Trend 📈";
      right: -38px;
      top: 75px;
    }
    section.social::before {
      content: "Social 🫂";
      right: -39px;
      top: 77px;
    }
    section.nature::before {
      content: "Nature 🌳";
      right: -43px;
      top: 90px;
    }
    section h1 {
      text-align: center;
    }
    article.post h2 {
      margin-top: 0;
      border: none;
    }
    figure p {
      text-align: center;
    }
    article.post figure img {
      max-height: 55mm;
      width: unset;
      max-width: 100%;
    }
    h3 {
      break-after: avoid;
      /* This isn't actually implemented yet,
      but one day it'll make the headers look nice */
    }
    article.post li {
      margin-bottom: 0.2em;
    }
    .footnotes {
      border-top: none;
      column-count: 2;
      padding: 1cm;
      page-break-before: always;
    }
    section td {
      text-align: center;
    }

  }
</style>

{%- comment -%}
From here down is the automatically generated content from the `cards`
sub-folder in the `_data` folder.
{%- endcomment -%}

{% for org_hash in site.data.cards %}
{% assign card = org_hash[1] %}

{% if card.live %}

<section class="card {{ card.card_type }}">

## {{ card.title }}

<figure>
![]({{ site.baseurl }}/assets/20/game/images/{{ card.image.source }})
<figcaption>{{ card.image.caption }} <a href="{{ card.image.link }}"><cite>{{ card.image.citation }}</cite></a>
</figcaption>
</figure>

{% for p in card.body.paragraphs %}
{{ p }}
{% endfor %}

### Consider

{% for p in card.consider %}

-   {{ p }}
{% endfor %}
</section>

{% for fn in card.footnotes %}
[^{{ fn[0] }}]: {{ fn[1]}}

{% endfor %}

{% endif %}

{% endfor %}
