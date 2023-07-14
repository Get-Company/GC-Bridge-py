
const app = Vue.createApp({
    data() {
        return {
            product: 'Socks-'
        }
    },
    methods: {
        make_it_reload() {
            console.log("Interval " + this.product);
            window.setInterval(this.product, 1000);
        }
    },
    computed: {
        make_product_reload() {
            return this.make_it_reload()
        }
    }
})

