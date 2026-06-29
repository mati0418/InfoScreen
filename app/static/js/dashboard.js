function formatDate(dateStr, mode = "weekday") {
    const d = new Date(dateStr);

    if (mode === "weekday") {
        return new Intl.DateTimeFormat("de-DE", {
            weekday: "long"
        }).format(d);
    }

    if (mode === "date") {
        return new Intl.DateTimeFormat("de-DE", {
            day: "2-digit",
            month: "long",
            year: "numeric"
        }).format(d);
    }

    return d.toString();
}

function formatTime(timeStr) {
    timeStr = timeStr.padStart(3, "0")
    return `${timeStr.slice(0, -2)}:${timeStr.slice(-2)}`
}

function updateTime() {
    const now = new Date();

    document.getElementById("current-time").innerHTML =
        `${now.getHours().toString().padStart(2,"0")}:` +
        `${now.getMinutes().toString().padStart(2,"0")}`;
}


// -------------------- WEATHER LOAD --------------------

async function loadWeather() {
    const res = await fetch("/weather");
    const data = await res.json();

    // CURRENT
    document.getElementById("current").innerHTML = `
        <div class="flex w-full items-center gap-6 mb-6">

            <i class="wi ${data.current.text} text-8xl"></i>

            <div class="text-6xl">${data.current.temp}°C</div>
        </div>

        <div class="text-4xl opacity-80">
            ${data.current.desc}
        </div>
    `;


    // FORECAST
    let forecastHtml = "";

    data.forecast.forEach((day, index) => {

        let hourlyHtml = "";

        day.hourly.forEach(hour => {
            hourlyHtml += `
                <div class="flex gap-8 bg-slate-700 p-4 rounded-lg w-full items-center shadow">
                    <div class="font-bold text-2xl w-1/6 text-right">
                        ${formatTime(hour.time)}
                    </div>

                    <i class="wi ${hour.text} text-4xl w-1/6"></i>

                    <div class="text-2xl opacity-80 w-3/6">
                        ${hour.desc}
                    </div>

                    <div class="text-2xl text-center w-1/6">
                        ${hour.temp}°
                    </div>
                </div>
            `;
        });

        forecastHtml += `
            <div class="forecast-card bg-slate-800 grid grid-cols-2 p-6 rounded-2xl xl:w-1/3 content-start shadow-lg hover:ring hover:ring-4 ring-slate-600"
                data-index="${index}"
            >

                <div class="font-bold mb-2 text-4xl text-center col-span-2 h-12">
                    ${formatDate(day.date)}
                </div>

                <i class="wi ${day.text} h-32 text-8xl text-center row-span-2 "></i>

                <div class="text-2xl h-16 opacity-80">
                    ${day.desc}
                </div>

                <div class="text-2xl h-16">
                    ${day.max}° / ${day.min}°
                </div>

                <div class="col-span-full">
                    ${hourlyHtml}
                </div>
            </div>
        `;
    });

    document.getElementById("forecast").innerHTML = forecastHtml;

    // FORECAST MODAL
    document.querySelectorAll(".forecast-card").forEach(card => {

        card.addEventListener("click", () => {

            const index = card.dataset.index;
            const day = data.forecast[index];

            let hourlyHtml = "";
            day.hourly.forEach(hour => {
                hourlyHtml += `
                    <div class="grid grid-cols-10 gap-8 bg-slate-700 p-4 rounded-lg w-full items-center shadow">

                        <div class="font-bold text-2xl w-1/16 text-right">
                            ${formatTime(hour.time)}
                        </div>

                        <i class="wi ${hour.text} text-6xl w-1/16"></i>

                        <div class="text-2xl opacity-80 w-2/16">
                            ${hour.desc}
                        </div>

                        <div class="text-2xl text-center w-1/16">
                            ${hour.temp}°C
                        </div>

                        <div class="text-2xl text-center w-2/16">
                            <i class="wi wi-day-sunny wi-uv text-5xl ${hour.uvColor}" data-uv="${hour.uvIndex}"></i>
                        </div>

                        <div class="text-2xl text-center w-2/16">
                            ${hour.rainChance}
                        </div>

                        <div class="text-2xl text-center w-2/16">
                            ${hour.precipMM}
                        </div>

                        <div class="text-2xl text-center w-2/16">
                            ${hour.visibility} km Sicht
                        </div>

                        <div class="text-end">
                            <i class="wi wi-wind wi-from-${hour.windDir.toLowerCase()} text-6xl size-fit"></i>
                        </div>

                        <i class="wi ${hour.windspeedtext} text-6xl w-1/16"></i>
                        

                    </div>
                `;
            });

            document.getElementById("modal-Content").innerHTML = `
            <div class="bg-slate-800 grid grid-cols-5 p-6 rounded-2xl w-full content-start shadow-lg relative">

                <div class="text-3xl font-bold text-center col-span-full place-content-center h-12">
                    ${formatDate(day.date)}  ${formatDate(day.date, "date")}
                </div>

                <div class="row-span-2 content-center text-right">
                    <i class="wi ${day.text} h-32 px-4 pb-4 text-8xl text-right place-content-center row-span-2 "></i>
                </div>

                <div class="text-2xl content-center text-center h-16 opacity-80">
                    ${day.desc}
                </div>
                
                <div class="grid grid-cols-2 justify-evenly w-40">
                    <i class="wi wi-sunrise text-yellow-400 place-content-center text-3xl text-right h-16"></i>
                    <div class="text-2xl h-16 text-right place-content-center">
                        ${formatTime(day.sunrise)}
                    </div>
                </div>

                <div class="grid grid-cols-2 justify-evenly w-40">
                    <i class="wi wi-moonrise text-yellow-400 place-content-center text-3xl text-right h-16"></i>
                    <div class="text-2xl h-16 text-right place-content-center">
                        ${formatTime(day.moonrise)}
                    </div>
                </div>

                <div class="row-span-2 place-content-center">
                    <i class="wi ${day.moonphase} text-yellow-400 h-32 px-4 text-8xl text-center place-content-center row-span-2"></i>
                </div>

                <div class="text-2xl content-center text-center h-16">
                    ${day.max}° / ${day.min}°
                </div>
            
                <div class="grid grid-cols-2 justify-evenly w-40">
                    <i class="wi wi-sunset text-yellow-400 text-3xl place-content-center text-right h-16"></i>
                    <div class="text-2xl h-16 text-right content-center">
                        ${formatTime(day.sunset)}
                    </div>
                </div>

                <div class="grid grid-cols-2 justify-evenly w-40">
                    <i class="wi wi-moonset text-yellow-400 text-3xl place-content-center text-right h-16"></i>
                    <div class="text-2xl h-16 text-right content-center">
                        ${formatTime(day.moonset)}
                    </div>
                </div>

                <!-- Stündliche Wetterdaten -->
                <div class="col-span-full">
                    ${hourlyHtml}
                </div>


            </div>
            `;

            document.getElementById("modal").classList.remove("hidden");
        })
    })

    document.getElementById("modal").addEventListener('click', (e) => {
        if (e.target === document.getElementById("modal")) {
            document.getElementById("modal").classList.add('hidden')
        }
    })
}


// -------------------- INIT --------------------

loadWeather();
updateTime();

setInterval(loadWeather, 300000);
setInterval(updateTime, 60000);
