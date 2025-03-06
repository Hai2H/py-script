// 发布到夸父资源
document.addEventListener('DOMContentLoaded', function() {
    var buttons = document.querySelectorAll('.fabu-kuafu');
            buttons.forEach(function(button) {
                button.addEventListener('click', function() {
                    var index = this.getAttribute('data-code');
                    var quake_href = document.getElementById('quake_new_href_'+ index).value;

                    // var quake_href = this.getAttribute('data-quake-new-href');
                    handleClick(index, quake_href);
                });
            });
    function handleClick(index, quake_href) {
        if (!quake_href) {
            alert('请先输入quake_href');
            return;
        }
        fetch("/repost/pushKuaFu?quake_href=" + quake_href + "&id=" + index)
            .then(response => response.text())
            .then(data => {
                console.log(data);
                alert(data);
            })
            .catch(error => {
                console.error('Error:', error);
            });
    }
});

document.addEventListener('DOMContentLoaded', function() {
            var inputs = document.querySelectorAll('.quake_new_href_input');
            inputs.forEach(function(input) {
                input.addEventListener('blur', function() {
                    var inputValue = this.value;
                    this.value = extractLink(inputValue);
                });
            });

            function extractLink(inputValue) {
                // 使用正则表达式匹配 URL
                var urlPattern = /(https?:\/\/[^\s]+)/g;
                var match = inputValue.match(urlPattern);
                if (match) {
                    return match[0];
                } else {
                    return '';
                }
            }
        });