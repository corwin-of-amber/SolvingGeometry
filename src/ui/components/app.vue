<template>
    <div id="app">
        <list-of-samples :data="samples"/>
    </div>
</template>

<script>
import listOfSamples from './list-of-samples.vue';

export default {
    props: ['samples'],
    components: { listOfSamples }
}
</script>

<style>

</style>