<template>
    <select v-model="selected">
        <option v-for="v, k in data" :key="k" :value="k">{{k}}</option>
    </select>
</template>

<script>
export default {
    props: ['data', 'initial'],
    data: () => ({selected: undefined}),
    mounted() {
        this.selected = this.initial ?? Object.keys(this.data)[0];
    },
    watch: {
        selected(v) {
            this.$emit('select', {name: v, content: this.data[v]});
        }
    },
}
</script>

<style>

</style>