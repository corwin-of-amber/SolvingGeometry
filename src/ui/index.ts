import * as Vue from 'vue';


// @ts-ignore
import mainUI from './components/app.vue';
import './index.css';


async function main() {
    var samples = await (await fetch('/samples')).json();

    var app = Vue.createApp(mainUI, {samples});
    app.mount('body');
}

document.addEventListener('DOMContentLoaded', () => main());