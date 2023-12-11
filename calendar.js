document.addEventListener('DOMContentLoaded', function() {
  var initialTimeZone = 'America/Los_Angeles';
  var calendarEl = document.getElementById('calendar');
  var timezoneSelectorEl = document.getElementById('timezone-selector');

  var calendar = new FullCalendar.Calendar(calendarEl, {
    timeZone: 'America/Los_Angeles', //defaults to LA time
    initialView: 'dayGridMonth',
    dayMaxEvents: true, // allow "more" link when too many events
    selectable: true,
    navLinks: true, // can click day/week names to navigate views
    // eventTimeFormat: { hour: 'numeric', minute: '2-digit', timeZoneName: 'short' },

    headerToolbar: {
      left: 'prev,next today',
      center: 'title',
      right: 'dayGridMonth,timeGridWeek,timeGridDay,listWeek',
    },

    // events: /get_events/+user_id,
      // events: [
      //   {
      //     title: 'BCH237',
      //     start: '2023-12-12T10:30:00',
      //     end: '2023-12-12T11:30:00',
      //     extendedProps: {
      //       department: 'BioChemistry'
      //     },
      //     description: 'Lecture'
      //   }
        // more events ...
      // ],

  });
  calendar.render();
 
  // Timezones for selector
  var timezones = [
    { value: 'America/Los_Angeles', text: 'Los Angeles' },
    { value: 'America/New_York', text: 'New York' },
    { value: 'Asia/Karachi', text: 'Karachi' },
    { value: 'Asia/Tokyo', text: 'Tokyo' },
    { value: 'Europe/Helsinki', text: 'Helsinki' },
  ];

  // Populate selector with options
  timezones.forEach(function(tz) {
    var optionEl = document.createElement('option');
    optionEl.value = tz.value;
    optionEl.innerText = tz.text;
    timezoneSelectorEl.appendChild(optionEl);
  });

  function refetchEvents() {
    fetch('/get_events/' + user_id)
      .then(response => response.json())
      .then(events => {
        calendar.removeAllEvents();
        calendar.addEventSource(events);
        calendar.rerenderEvents();
      });
  }
  
  
  // Initially fetch and render events 
  refetchEvents();

  // Re-fetch events on some trigger
  document.addEventListener('someTrigger', refetchEvents);

  // fetch('/get_events/1')
  //   .then((response) => response.json())
  //   .then((timeZones) => {
  //     timeZones.forEach(function(timeZone) {
  //       var optionEl;

  //       if (timeZone !== 'UTC') { // UTC is already in the list
  //         optionEl = document.createElement('option');
  //         optionEl.value = timeZone;
  //         optionEl.innerText = timeZone;
  //         timezoneSelectorEl.appendChild(optionEl);
  //       }
  //     });
  //   });

  // When selector changes, update timezone
  timezoneSelectorEl.addEventListener('change', function() {
    calendar.setOption('timeZone', this.value);

    // calendar.render();
  });


});




// commented out test events:
    // events: [
    //   {
    //     title: 'Kicking a Dog',
    //     start: '2023-12-09T10:00',
    //     end: '2023-12-09T12:00',
    //     color: 'purple',

    //   },
    //   {
    //     title: 'new event 2',
    //     start: '2023-12-09T11:00',
    //     end: '2023-12-09T13:00',
    //     color: 'orange',
    //   },
    //   {
    //     title: 'Event in Tokyo 3',
    //     start: '2023-12-09T12:00',

    //   },
    //   {
    //     title: 'Event 4',
    //     start: '2023-12-09T13:00',

    //   },
    //   {
    //     title: 'Event 5',
    //     start: '2023-12-09T15:00',

    //   },
    //   {
    //     title: 'Event 6',
    //     start: '2023-12-09T15:00',

    //   },
    //   {
    //     title: 'Event 7',
    //     start: '2023-12-09T15:00',

    //   },
    // ],