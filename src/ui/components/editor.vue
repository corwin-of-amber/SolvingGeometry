<template>
    <div>
    </div>
</template>

<script>
import { CodeMirror } from '../infra/cm6-easy';


export default {
    mounted() {
        var el = this.$el;
        this.cm = new CodeMirror(el);
    },
    methods: {
        open(name, defaultContent) {
            this.cm.setValue(defaultContent);
        }
    }
}
</script>

<style>

</style>