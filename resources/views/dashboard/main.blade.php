@extends('layout.main')

@section('container')
    @include('partials.navbar')

    <script src="https://cdn.jsdelivr.net/npm/apexcharts"></script>
    <section class="flex h-screen w-screen items-center justify-center p-12" id="signIn">

        <div class="z-[-1] mt-32 flex h-full w-full flex-col items-start justify-between">
            <div class="flex w-full gap-4">

                <!-- Stacked Bar Chart - Jumlah Perusahaan Berdasarkan Sektor dan Tahun -->
                <div class="mb-8 h-[55vh] w-[55vw] rounded-md bg-white p-5 shadow-lg shadow-secondary">
                    <h1 class="mb-3 text-base font-semibold">Top 5 Jumlah Perusahaan Berdasarkan Sektor dan Tahun</h1>
                    <div class="h-[80%] w-full" id="stacked-bar-chart"></div>
                    <script>
                        var categories = @json($categories); // Tahun
                        var formattedData = @json($formattedData); // Data formatted dari controller

                        // Siapkan series data untuk chart
                        var seriesData = [];
                        Object.keys(formattedData).forEach(function(sektor) {
                            var dataSeries = [];
                            categories.forEach(function(tahun) {
                                dataSeries.push(formattedData[sektor][tahun] || 0); // Isi 0 jika tidak ada data
                            });
                            seriesData.push({
                                name: sektor,
                                data: dataSeries
                            });
                        });

                        var stackedBarOptions = {
                            chart: {
                                type: 'bar',
                                stacked: true,
                                width: '100%',
                                height: 400,
                                toolbar: {
                                    show: true,
                                    tools: {
                                        download: true,
                                        selection: true,
                                        zoom: true,
                                        zoomin: true,
                                        zoomout: true,
                                        pan: true,
                                        reset: true,
                                        customIcons: []
                                    }
                                }
                            },
                            series: seriesData,
                            xaxis: {
                                categories: categories,
                                title: {
                                    text: 'Tahun'
                                }
                            },
                            yaxis: {
                                title: {
                                    text: 'Jumlah Perusahaan'
                                }
                            },
                            colors: [
                                '#D3D3D3',
                                '#A9B5C9',
                                '#819EB9',
                                '#4B6A9B',
                                '#2D3945',
                            ],
                            plotOptions: {
                                bar: {
                                    horizontal: false,
                                    columnWidth: '55%',
                                    endingShape: 'rounded'
                                }
                            },
                            dataLabels: {
                                enabled: false
                            },
                            legend: {
                                position: 'bottom'
                            }
                        }

                        var stackedBarChart = new ApexCharts(document.querySelector("#stacked-bar-chart"), stackedBarOptions);
                        stackedBarChart.render();
                    </script>
                </div>
                <div class="flex h-[55vh] w-[45vw] flex-col">
                    <div class="mb-4 flex h-1/2 w-full">
                        <div class="mr-4 h-full w-1/2 rounded-md bg-white p-5 shadow-lg shadow-secondary">
                            <h1 class="text-base font-extrabold sm:text-sm md:text-base lg:text-lg">Pertumbuhan Produksi
                                <br>(Kecil dan Mikro)
                            </h1>
                            <br>
                            <p class="text-justify text-base">Peningkatan output atau hasil produksi dalam sektor industri
                                manufaktur dari waktu ke waktu.</p>
                        </div>
                        <div class="ml-4 h-full w-1/2 rounded-md bg-white p-5 shadow-lg shadow-secondary">
                            <h1
                                class="bg-gradient-to-tl from-secondary to-primary bg-clip-text text-base font-extrabold text-transparent sm:text-sm md:text-base lg:text-2xl">
                                Manufachub</h1>
                            <br>
                            <h1 class="text-justify text-base font-semibold sm:text-sm md:text-base lg:text-lg">Dashboard
                                ini menyajikan
                                data kinerja industri manufaktur kecil dan mikro, termasuk
                                distribusi
                                perusahaan dan pertumbuhan produksi untuk mendukung pengambilan keputusan strategis.</h1>
                        </div>
                    </div>
                    <div class="mt-4 flex h-1/2 w-full">
                        <div class="mr-4 h-full w-1/2 rounded-md bg-white p-5 shadow-lg shadow-secondary">
                            <h1 class="text-base font-extrabold sm:text-sm md:text-base lg:text-lg">Nilai Output <br>(Kecil
                                dan Mikro)</h1>
                            <br>
                            <p class="text-justify text-base">Selisih antara nilai produk jadi dan biaya bahan baku,
                                mencerminkan
                                efisiensi
                                dan produktivitas industri dalam menghasilkan output bernilai tinggi.</p>
                        </div>
                        <div class="ml-4 h-full w-1/2 rounded-md bg-white p-5 shadow-lg shadow-secondary">
                            <h1 class="text-base font-extrabold sm:text-sm md:text-base lg:text-lg">Nilai Tambah
                                Industri <br>(Kecil dan Mikro)</h1>
                            <br>
                            <p class="text-justify text-base">Biaya tambahan dalam produksi, termasuk tenaga kerja, energi,
                                dan overhead, yang diperlukan untuk meningkatkan nilai produk jadi dari bahan baku.</p>
                        </div>
                    </div>
                </div>
            </div>

            <div class="flex w-full gap-4">
                <div class="h-[45vh] w-[60vw] rounded-md bg-white p-4 shadow-lg shadow-secondary">
                    <!-- Pertumbuhan Produksi Berdasarkan Tahun Chart -->
                    <div class="mb-5 h-auto w-full">
                        <h1 class="text-base font-semibold sm:text-sm md:text-base lg:text-lg">Pertumbuhan Produksi
                            DKI Jakarta, Bali, dan Jawa Timur Berdasarkan Tahun</h1>
                    </div>
                    <div class="z-10 h-auto w-full" id="area-chart"></div>

                    <script>
                        // Data dari controller
                        var seriesData2 = @json($seriesData2);
                        var categories3 = @json($categories3);

                        var areaChartOptions = {
                            chart: {
                                type: 'area',
                                height: 320,
                                width: '100%',
                                toolbar: {
                                    show: true
                                }
                            },
                            series: seriesData2,
                            xaxis: {
                                categories: categories3,
                                title: {
                                    text: 'Tahun'
                                }
                            },
                            yaxis: {
                                title: {
                                    text: 'Persentase Pertumbuhan Produksi'
                                }
                            },
                            colors: [
                                '#2D3945',
                                '#4B6A9B',
                                '#819EB9',
                                '#A9B5C9',
                                '#D3D3D3',
                            ],
                            dataLabels: {
                                enabled: false
                            },
                            stroke: {
                                curve: 'smooth'
                            },
                            fill: {
                                type: 'gradient',
                                gradient: {
                                    shadeIntensity: 1,
                                    opacityFrom: 0.7,
                                    opacityTo: 0.9,
                                    stops: [0, 90, 100]
                                }
                            },
                            legend: {
                                position: 'top',
                                horizontalAlign: 'center'
                            },
                            tooltip: {
                                shared: true,
                                intersect: false
                            },
                            grid: {
                                padding: {
                                    left: 0,
                                    right: 0,
                                    bottom: 0,
                                    top: 0
                                }
                            }
                        };

                        var areaChart = new ApexCharts(document.querySelector("#area-chart"), areaChartOptions);

                        areaChart.render();
                    </script>
                </div>

                <!-- Nilai Tambah Industri Berdasarkan Provinsi dan Sektor Industri Chart -->
                <div class="h-[45vh] w-[40vw] rounded-md bg-white p-5 shadow-lg shadow-secondary">
                    <div class="mb-5 h-auto w-full">
                        <h1 class="text-base font-semibold sm:text-sm md:text-base lg:text-lg">
                            Top 5 Nilai Tambah Industri Berdasarkan Sektor Industri dan Skala Industri
                        </h1>
                    </div>
                    <div class="h-auto w-full" id="clustered-bar-chart"></div>

                    <script>
                        var categories = @json($categories2);
                        var formattedData = @json($formattedData2);

                        var seriesData = [];
                        Object.keys(formattedData).forEach(function(sektor) {
                            var dataSeries = [];
                            categories.forEach(function(skala) {
                                dataSeries.push(formattedData[sektor][skala] || 0);
                            });
                            seriesData.push({
                                name: sektor,
                                data: dataSeries
                            });
                        });

                        var clusteredBarOptions = {
                            chart: {
                                type: 'bar',
                                width: '100%',
                                height: 290,
                                stacked: false,
                                toolbar: {
                                    show: true,
                                    tools: {
                                        download: true,
                                        selection: true,
                                        zoom: true,
                                        zoomin: true,
                                        zoomout: true,
                                        pan: true,
                                        reset: true,
                                        customIcons: []
                                    }
                                }
                            },
                            series: seriesData,
                            xaxis: {
                                categories: categories,
                                title: {
                                    text: 'Tahun'
                                }
                            },
                            yaxis: {
                                title: {
                                    text: 'Nilai Tambah Industri'
                                }
                            },
                            colors: [
                                '#2D3945',
                                '#4B6A9B',
                                '#819EB9',
                                '#A9B5C9',
                                '#D3D3D3',
                            ],
                            legend: {
                                position: 'bottom'
                            },
                            plotOptions: {
                                bar: {
                                    horizontal: false,
                                    columnWidth: '40%',
                                    endingShape: 'rounded'
                                }
                            },
                            dataLabels: {
                                enabled: false
                            },
                            grid: {
                                padding: {
                                    top: 0,
                                    right: 0,
                                    bottom: 0,
                                    left: 0
                                }
                            }
                        };

                        var clusteredBarChart = new ApexCharts(document.querySelector("#clustered-bar-chart"), clusteredBarOptions);
                        clusteredBarChart.render();
                    </script>
                </div>
            </div>

            <div class="mt-5 flex w-full gap-4">
                <div class="h-[36vh] w-4/12 rounded-md bg-white p-5 shadow-lg shadow-secondary">
                    <!-- Perbandingan Total Nilai Output Berdasarkan Skala -->
                    <h1 class="text-md mbbase font-semibold">Perbandingan Total Nilai Output Berdasarkan Skala</h1>
                    <div class="h-[80%] w-full" id="grouped-bar-chart"></div>
                    <script>
                        var outputKecil = [{{ $outputKecil }}];
                        var outputMikro = [{{ $outputMikro }}];
                        var groupedBarOptions = {
                            chart: {
                                type: 'bar',
                                height: 275,
                                width: '100%',
                                toolbar: {
                                    show: true
                                }
                            },
                            series: [{
                                    name: 'Skala Kecil',
                                    data: outputKecil
                                },
                                {
                                    name: 'Skala Mikro',
                                    data: outputMikro
                                }
                            ],
                            xaxis: {
                                categories: [''],
                                title: {
                                    text: 'Skala'
                                }
                            },
                            yaxis: {
                                title: {
                                    text: 'Nilai Output'
                                }
                            },
                            plotOptions: {
                                bar: {
                                    horizontal: false,
                                    columnWidth: '50%',
                                    endingShape: 'rounded'
                                }
                            },
                            colors: [
                                '#4B6A9B',
                                '#2D3945',
                                '#819EB9',
                                '#A9B5C9',
                                '#D3D3D3',
                            ],
                            dataLabels: {
                                enabled: true
                            },
                            legend: {
                                position: 'top'
                            }
                        };

                        var groupedBarChart = new ApexCharts(document.querySelector("#grouped-bar-chart"), groupedBarOptions);
                        groupedBarChart.render();
                    </script>
                </div>

                <!-- Nilai Output Berdasarkan Sektor Industri Chart -->
                <div class="h-[36vh] w-9/12 rounded-md bg-white p-5 shadow-lg shadow-secondary">
                    <div class="mb-5 h-auto w-full">
                        <h1 class="text-base font-semibold sm:text-sm md:text-base lg:text-lg">Top 5 Nilai Output
                            Berdasarkan Sektor Industri</h1>
                    </div>
                    <div class="h-auto w-full" id="horizontal-bar-chart"></div>

                    <script>
                        // Data dari controller
                        var categories5 = @json($categories5); // Nama sektor industri
                        var outputValues = @json($outputValues); // Nilai output untuk masing-masing sektor

                        var barOptions = {
                            chart: {
                                type: 'bar',
                                width: '100%',
                                height: 250,
                                toolbar: {
                                    show: true
                                }
                            },
                            plotOptions: {
                                bar: {
                                    horizontal: true,
                                    barHeight: '70%',
                                    dataLabels: {
                                        position: 'top'
                                    }
                                }
                            },
                            series: [{
                                name: 'Nilai Output',
                                data: outputValues, // Nilai output untuk top 5 sektor
                                color: function({
                                    value,
                                    seriesIndex,
                                    dataPointIndex,
                                    w
                                }) {
                                    var colors = ['#2D3945', '#4B6A9B', '#819EB9', '#A9B5C9', '#D3D3D3'];
                                    return colors[dataPointIndex % colors.length];
                                }
                            }],
                            xaxis: {
                                categories: categories5, // Nama sektor industri
                                title: {
                                    text: 'Nilai Output'
                                }
                            },
                            yaxis: {
                                title: {
                                    text: 'Sektor Industri'
                                }
                            },
                            dataLabels: {
                                enabled: true,
                                formatter: function(val) {
                                    return val;
                                },
                                offsetX: 10,
                                style: {
                                    fontSize: '12px',
                                    colors: ['#000']
                                }
                            },
                            grid: {
                                padding: {
                                    top: 0,
                                    right: 0,
                                    bottom: 0,
                                    left: 0
                                }
                            },
                            legend: {
                                show: false
                            }
                        };

                        var horizontalBarChart = new ApexCharts(document.querySelector("#horizontal-bar-chart"), barOptions);
                        horizontalBarChart.render();
                    </script>
                </div>

            </div>

            {{-- <div class="mb-10 mt-5 flex w-full gap-4">
                <div class="h-[45vh] w-3/12 rounded-md bg-white p-5 shadow-lg shadow-secondary">
                    <!-- Jumlah Perusahaan Berdasarkan Skala Industri Chart -->
                    <div class="mb-5 h-auto w-full">
                        <h1 class="text-base font-semibold sm:text-sm md:text-base lg:text-lg">Jumlah Perusahaan Berdasarkan
                            Skala Industri</h1>
                    </div>
                    <div class="h-auto w-full" id="donut-chart"></div>

                    <script>
                        // Data dari controller
                        var seriesData = @json($seriesData); // Jumlah perusahaan per skala
                        var labels = @json($labels); // Nama skala industri

                        var donutOptions = {
                            chart: {
                                type: 'donut',
                                width: '100%',
                                height: 350,
                                toolbar: {
                                    show: true
                                }
                            },
                            series: seriesData, // Data jumlah perusahaan
                            labels: labels, // Nama skala industri
                            colors: [
                                '#4B6A9B',
                                '#2D3945',
                                '#819EB9',
                                '#A9B5C9',
                                '#D3D3D3',
                            ],
                            dataLabels: {
                                enabled: true
                            },
                            legend: {
                                position: 'bottom'
                            }
                        }

                        var donutChart = new ApexCharts(document.querySelector("#donut-chart"), donutOptions);

                        donutChart.render();
                    </script>
                </div>

               
                <div class="h-[45vh] w-9/12 rounded-md bg-white p-5 shadow-lg shadow-secondary">
                    
                </div>

            </div> --}}
        </div>
    </section>
@endsection
