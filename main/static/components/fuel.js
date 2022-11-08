app.component('fuel-card', {
    template:
    /*html*/
        `<div class="card bg-light">
    <div class="card-header">
        <h5 class="card-title display-6">
            Tanken
        </h5>
    </div>
    <div class="card-body table-responsive">
        <table class="table">
            <thead>
            <tr>
                <th>Kraftstoffart </th>
                <th>{{hem.brand}}</th>
                <th>{{total.brand}}</th>
            </tr>
            </thead>
            <tbody>
            <tr>
                <td>Diesel:</td>
                <td>{{hem.diesel}} €</td>
                <td>{{total.diesel}} €</td>
            </tr>
            <tr>
                <td>E10:</td>
                <td>{{hem.e10}} €</td>
                <td>{{total.e10}} €</td>
            </tr>
            </tbody>
        </table>
    </div>
    <div class="card-footer">
            <p>Nächster Sync: {{countDownDateString}} Uhr</p>
    </div>
</div>`,
    data() {
        return {
            hem: '-waiting-',
            total: '-waiting-',
            station: '-waiting-',
            hem_url: 'https://creativecommons.tankerkoenig.de/json/detail.php?id=2254b8cd-866b-49df-bd54-cbc36c2e7ed6&apikey=c351dfbf-8f6f-a4d2-0c2d-a255d25a0075',
            total_url: 'https://creativecommons.tankerkoenig.de/json/detail.php?id=22aed561-5146-4ebe-94dd-6242aad2f079&apikey=c351dfbf-8f6f-a4d2-0c2d-a255d25a0075',
            /* In Min. */
            sync_interval: 1,
            refresh: 1000 * 60 * 60,
            counter: 0.5 * 60 * 60,
            countDownDate: new Date().getTime(),
            countDownDateString: '00:00'
        }
    },
    created() {
        this.countDown();
        this.setTime();
        this.getFuel();


    },
    methods: {
        countDown() {
            this.counter -= 1;
        },
        setTime() {
            updated_time = new Date(this.countDownDate + this.counter * 1000);
            this.countDownDate = updated_time;
            this.countDownDateString = this.countDownDate.toLocaleTimeString();
        },
        async getFuel() {
            this.setTime();
            try{
                let response_hem = await fetch(this.hem_url);
                let data_hem = await response_hem.json();
                this.hem = data_hem.station;

                let response_total = await fetch(this.total_url);
               let data_total = await response_total.json();
                this.total = data_total.station
            }catch(err){
                console.error(err);
                }
            }
    },
    mounted() {
        setInterval(this.countDown, 1000);
        /* func, delay, arg1, arg2, arg... */
        setInterval(this.getFuel, this.refresh);
    }

})