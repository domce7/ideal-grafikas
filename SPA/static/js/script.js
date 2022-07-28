// creating needed vars
currentYear = new Date().getFullYear();
currentMonth = new Date().getMonth() + 1;

// first year option is created and chosen as a default
optionYearOne = document.getElementById('opt-year-1');
optionYearOne.textContent = currentYear;
optionYearOne.value = currentYear;
optionYearOne.setAttribute('selected', 'selected');

// following year option is created
optionYearTwo = document.getElementById('opt-year-2');
optionYearTwo.textContent = currentYear+ 1;
optionYearTwo.value = currentYear + 1;


// month select options are created
selectMonth = document.getElementById('select-month');
// default month is the following month
for (i = 0; i < selectMonth.options.length; i++) {
    if (i === currentMonth){
        selectMonth.options[i].setAttribute('selected', 'selected');
    }
}





