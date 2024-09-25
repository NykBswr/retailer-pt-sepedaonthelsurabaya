@extends('layout.main')

@section('container')
    @include('partials.navbar')

    <section class="pt-22 flex h-full w-screen items-center justify-center px-5" id="Kelompok">
        <div class="mt-24 flex h-full w-full flex-col items-center justify-between rounded-md">
            <div class="mt-5 flex h-auto w-full flex-col items-center justify-center">
                <h1
                    class="bg-gradient-to-tl from-secondary to-primary bg-clip-text text-center text-[4.1vw] font-extrabold text-transparent">
                    Meet our Team</h1>
                <p class="mt-2 w-[45vw] text-center text-xs text-dark sm:text-sm md:text-base lg:text-xl">
                    Get to know Group G from the Enterprise Application Integration SD-A1 course!
                </p>
            </div>

            <div class="flex h-full w-full items-center justify-between pt-10">
                <!-- Card 1 -->
                <div class="flex h-full w-full items-center justify-between pt-10">
                    <style>
                        .group:hover~.card-3 .img {
                            filter: grayscale(100%);
                        }

                        .group2:hover~.card-3 .img {
                            filter: grayscale(100%) !important;
                        }
                    </style>
                    <!-- Card 1 -->
                    <div class="group flex h-[40vh] w-[17.8vw] items-end rounded-md bg-gray-100 shadow-lg hover:z-10">
                        <img class="img h-full w-full rounded-md grayscale transition duration-300 group-hover:grayscale-0"
                            src="{{ asset('img/diaz.png') }}" alt="DIAZ ARVINDA ARDIAN">
                        <div
                            class="absolute z-[1] mb-4 ml-4 h-auto w-[14.5vw] rounded bg-white px-3 py-2 text-justify text-dark shadow">
                            <h3 class="text-sm font-bold md:text-base lg:text-lg">Diaz Arvinda Ardian</h3>
                            <p class="text-dark">162112133009</p>
                        </div>
                    </div>

                    <!-- Card 2 -->
                    <div class="group flex h-[40vh] w-[17.5vw] items-end rounded-md bg-gray-100 shadow-lg hover:z-10">
                        <img class="img h-full w-full rounded-md grayscale transition duration-300 group-hover:grayscale-0"
                            src="{{ asset('img/richard.png') }}" alt="RICHARD HASANNAIN MONGIDE">
                        <div
                            class="absolute z-[1] mb-4 ml-4 h-auto w-[14.5vw] rounded bg-white px-3 py-2 text-justify text-dark shadow">
                            <h3 class="text-sm font-bold md:text-base lg:text-lg">Richard Hasannain Mongide</h3>
                            <p class="text-dark">162112133056</p>
                        </div>
                    </div>

                    <!-- Card 3 (Default without grayscale) -->
                    <div id="card-3"
                        class="card-3 flex h-[40vh] w-[17vw] items-end rounded-md bg-gray-100 shadow-lg hover:z-10">
                        <img id="img-3" class="img h-full w-full rounded-md grayscale-0 transition duration-300"
                            src="{{ asset('img/nyk.png') }}" alt="Nayaka Baswara">
                        <div
                            class="absolute z-[1] mb-4 ml-4 h-auto w-[14.5vw] rounded bg-white px-3 py-2 text-justify text-dark shadow">
                            <h3 class="text-sm font-bold md:text-base lg:text-lg">Nayaka Baswara</h3>
                            <p class="text-dark">162112133065</p>
                        </div>
                    </div>

                    <!-- Card 4 -->
                    <div
                        class="group2 group flex h-[40vh] w-[17.5vw] items-end rounded-md bg-gray-100 shadow-lg hover:z-10">
                        <img class="img h-full w-full rounded-md grayscale transition duration-300 group-hover:grayscale-0"
                            src="{{ asset('img/dara.png') }}" alt="Dara Devinta Faradhilla">
                        <div
                            class="absolute z-[1] mb-4 ml-4 h-auto w-[14.5vw] rounded bg-white px-3 py-2 text-justify text-dark shadow">
                            <h3 class="text-sm font-bold md:text-base lg:text-lg">Dara Devinta Faradhilla</h3>
                            <p class="text-dark">164221002</p>
                        </div>
                    </div>

                    <!-- Card 5 -->
                    <div
                        class="group2 group flex h-[40vh] w-[17.8vw] items-end rounded-md bg-gray-100 shadow-lg hover:z-10">
                        <img class="img h-full w-full rounded-md grayscale transition duration-300 group-hover:grayscale-0"
                            src="{{ asset('img/zhiddan.png') }}" alt="Zhiddan Aditya Mahardika">
                        <div
                            class="absolute z-[1] mb-4 ml-4 h-auto w-[14.5vw] rounded bg-white px-3 py-2 text-justify text-dark shadow">
                            <h3 class="text-sm font-bold md:text-base lg:text-lg">Zhiddan Aditya Mahardika</h3>
                            <p class="text-dark">164221086</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>
    <script>
        const cards = document.querySelectorAll('.group');
        const card3Image = document.getElementById('img-3');

        // Saat card lain di-hover, terapkan grayscale ke Card 3
        cards.forEach(card => {
            card.addEventListener('mouseover', () => {
                card3Image.classList.add('grayscale');
            });

            card.addEventListener('mouseout', () => {
                card3Image.classList.remove('grayscale');
            });
        });
    </script>
@endsection
