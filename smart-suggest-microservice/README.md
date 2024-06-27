# Smart Suggest Microservice

Author: Leonidas Avdelas

## Previous repository

[Here](https://gitlab.com/LoniasGR/smart-suggest-microservice)

## Description

This service works hand in hand with a Rasa server to provide suggestions on future discussion directions.

## Usage

To use it with Theano,

1) Checkout branch [143](https://gitlab.com/ilsp-spmd-all/public/covid-va-chatbot/-/merge_requests/143) of Theano.
2) Start the Rasa chat bot, as per instructions.
3) Run this service with `docker compose up -d`. It should attach itself to the common docker network and interoperate without issues.
