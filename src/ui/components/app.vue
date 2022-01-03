<template>
    <div id="app">
        <div class="pane" id="left-pane">
            <div id="list-of-samples-container">
                <list-of-samples :data="samples" @select="sampleSelected"/>
            </div>
            <div id="editor-container">
                <editor ref="editor"/>
            </div>
            <div id="compiler-out-container">
            </div>
        </div>
        <div class="pane" id="main-pane">
        </div>
    </div>
</template>

<script>
import Editor from './editor.vue';
import listOfSamples from './list-of-samples.vue';

export default {
    props: ['samples'],
    methods: {
        sampleSelected(ev) {
            this.$refs.editor.open(ev.name, ev.content.join('\n'));
        }
    },
    components: { listOfSamples, Editor }
}
</script>

<style>

</style>