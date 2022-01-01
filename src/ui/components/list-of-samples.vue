<template>
    <ul>
        <li v-for="v, k in data" :key="k">{{k}}</li>
    </ul>
</template>

<script>
export default {
    props: ['data']
}
</script>

<style>

</style>